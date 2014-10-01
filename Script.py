#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
from pyadb import ADB


#Afin de récuperer la db des sms sur le gsm! attention, adb requis
adb = ADB()
adb.set_adb_path('adb')

cmd = "su -c 'cat /data/data/com.android.providers.telephony/databases/mmssms.db > /sdcard/mmssms.db'"
adb.shell_command(cmd)

adb.get_remote_file('/sdcard/mmssms.db','./')

cmd = "su -c 'rm /sdcard/mmssms.db'"  
adb.shell_command(cmd)

con = lite.connect('mmssms.db')
cur = con.cursor()
result = cur.execute("SELECT CAST(body AS INTEGER), COUNT(DISTINCT(address)) FROM sms WHERE CAST(body AS INTEGER) BETWEEN 1 AND 80 GROUP BY CAST(body AS INTEGER)")


for kot, votes in list(result):
	print "Kot {}: {}".format(kot, votes)
	



    
