Sms-Vote
========

Programme des statistiques utilisé pour les 24h Vélo de LLN. 

Depedances
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
