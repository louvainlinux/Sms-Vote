## Important notice
Because this repository has not seen any activity in more than two years, it has been **archived** by the Louvain-li-Nux team in november 2019. It is now read-only, but you can still fork it. The terms of licence still apply.

Sms-Vote
========

Programme des statistiques utilisé pour les 24h Vélo de LLN. 

Dependances
==========
``` bash
sudo apt-get install android-tools-adb
sudo pip install pyadb
sudo apt-get install sqlite3
```

Utilisation
===========
Modifier la variable 
```
smartphone_addr = "192.168.1.4"
```
Avec l'adresse IP de votre smartphone Android


Vous devez aussi modifier le fichier kap.list avec la liste des participants. Le format est simple:
```
id_participant  nom
```
(séparés par des tabulations)
