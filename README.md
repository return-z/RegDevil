# RegDevil
Python script to abuse weak Windows Registry permissions

This script is only for educational purposes. No harm is intended, just spreading knowledge.
This script can help you priv-esc from an Authenticated user to the Administrator on a Windows machine. It works when registry permissions are weakly set, and the user has full control on registry.

Functions:
* This script can help you enumerate vulnerable services (which run as admin and are restartable manually)
* Help you deploy a temporary admin shell on the machine
* Help in deploying a persistent backdoor on the target

The script requires presence of netcat (nc.exe) in the folder C:\Windows\System32\spool\drivers\color\ of the target as it is generally whitelisted by AppLocker
