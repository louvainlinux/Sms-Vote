#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from pyadb import ADB
import time
import copy
import re

smartphone_addr = "192.168.1.4"


def get_kap_list():
	kot_list = {}
	with open('./kap.list') as kot_list_f:
		data = kot_list_f.read()
		data = data.split("\n")
		for kap in data:
			if kap == '':
				continue
			kap = kap.split("\t")
			kot_list[int(kap[0])] = kap[1]
	return kot_list

def update_db():
	adb = ADB()
        adb.set_adb_path('adb')

	adb.connect_remote(smartphone_addr)

        cmd = "su -c 'cat /data/data/com.android.providers.telephony/databases/mmssms.db > /sdcard/mmssms.db'"
        adb.shell_command(cmd)

	cmd = "su -c 'cat /data/data/com.android.providers.telephony/databases/mmssms.db-journal > /sdcard/mmssms.db-journal'"
        adb.shell_command(cmd)
	

        adb.get_remote_file('/sdcard/mmssms.db','./')
	adb.get_remote_file('/sdcard/mmssms.db-journal','./')

        cmd = "su -c 'rm /sdcard/mmssms.db'"
	adb.shell_command(cmd)
	cmd = "su -c 'rm /sdcard/mmssms.db-journal'"
        adb.shell_command(cmd)

def get_votes():
	update_db()

	con = lite.connect('mmssms.db')
	cur = con.cursor()
	result = cur.execute("SELECT CAST(body AS INTEGER), COUNT(DISTINCT(address)) FROM sms WHERE CAST(body AS INTEGER) BETWEEN 0 AND 100 GROUP BY CAST(body AS INTEGER)")

	votes = {a:b for a,b in list(result)}
	return votes

def update_votes(old_votes, old_addresses, last_id, kap_list, display_duplicate=False, display_error=True):
	update_db()

	new_votes = copy.deepcopy(old_votes)
	new_addresses = copy.deepcopy(old_addresses)

	con = lite.connect('mmssms.db')
        cur = con.cursor()

	result = cur.execute("SELECT `_id`, `body`, `address` FROM sms WHERE `_id` > {}".format(int(last_id)))

	max_id = last_id
	to_display = []
	for sms_id, body, address in result:
		max_id = max(max_id, sms_id)
		try:
			body = int(re.sub(r"^[^0-9]*([0-9]+)([^0-9]+.*)*$",r"\1",body))
		except:
			if display_error:
				try:
					to_display.append(str("\t- SMS invalide: {}".format(body)))
				except:
					to_display.append("\t- SMS invalide: non-affichable (UTF-8 incorrect?)")
			continue
		if body not in kap_list:
			if display_error:
				to_display.append("\t- KAP inconnu: {}".format(body))
			continue
		if (address, body) in new_addresses:
			if display_duplicate:
				to_display.append("\t- Le numero {} a deja vote pour le KAP {}".format(address, body))
			continue
		new_addresses.add((address, body))
		new_votes[body] = new_votes[body]+1 if body in new_votes else 1

	if len(to_display) != 0:
		print "---- Erreurs de lecture ----"
		print "\n".join(to_display)

	return (new_votes, new_addresses, max_id)

def get_place(vote_list):
	ordered_list = sorted(vote_list.iteritems(), key=lambda x: -x[1])
	return_list = {}
	current = 0
	old_val = -1
	for kot, votes in ordered_list:
		if votes != old_val:
			current = current + 1
			old_val = votes
		return_list[kot] = (current, votes)
	return return_list

def print_all(kot_list, vote_list, old_vote_list):
	ordered_old = get_place(old_vote_list)
	ordered_new = get_place(vote_list)
	fichier = open("classement.txt", "a") # Ouvre le fichier.
	fichier.write("---- Classement ----\n") # Ecris la réponse qui a été tapée.
	
	print "---- Classement ----"
	last_displayed_place = -1
	for kot, (place, votes) in sorted(ordered_new.iteritems(),key=lambda x: x[1][0]):
		if kot not in kot_list:
			continue
		old_place = ordered_old[kot][0] if kot in ordered_old else (len(ordered_new)+1)
		if old_place < place:
			place_indicator = "↓"
		elif old_place == place:
			place_indicator = "="
		else:
			place_indicator = "↑"
		if last_displayed_place == place:
			displayed_place = ""
		else:
			displayed_place = str(place)+"."
			last_displayed_place = place
		fichier.write("{}\t{}\t{}\t{} ({})\n".format(displayed_place, place_indicator, votes, kot_list[kot], kot))
		print "{}\t{}\t{}\t{} ({})".format(displayed_place, place_indicator, votes, kot_list[kot], kot)
	fichier.close() # Ferme le fichier

def compare_votes(oldl,newl,kap_list):
	to_display = []

	ordered_old = get_place(oldl)
	ordered_new = get_place(newl)
	for kap in newl:
		if kap not in kap_list:
			continue
		newv = ordered_new[kap][1]
		newp = ordered_new[kap][0]
		oldv = ordered_old[kap][1] if kap in oldl else 0
		oldp = ordered_old[kap][0] if kap in oldl else (len(oldl)+1)
		if newv != oldv:
			to_display.append("\t{}({}) a gagné {} vote(s). Total {}".format(kap_list[kap], kap, newv-oldv, newv))
			if newp != oldp:
				to_display.append("\t\tEst maintenant à la place {}! (avant: {})".format(newp, oldp))
	if len(to_display) != 0:
		print "--- Nouveaux votes comptabilisés ---"
		print "\n".join(to_display)

kot_list = get_kap_list()

vote_list, addresses, last_id = update_votes({}, set(), -1, kot_list)
old_vote_list = vote_list
count = 0
print_all(kot_list, vote_list, old_vote_list)
while True:
	time.sleep(30)
	count = count + 1
	new_vote_list, addresses, last_id = update_votes(vote_list, addresses, last_id, kot_list, True, True)
	compare_votes(vote_list, new_vote_list, kot_list)
	vote_list = new_vote_list
	if count % 10 == 0:
		print_all(kot_list, vote_list, old_vote_list)
		old_vote_list = vote_list
    
