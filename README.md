# CertifyTheWeb-DNS01-Plesk
 Create Let's Encrypt Certificate with DNS-01 challenge on Plesk  
 
 Based on https://github.com/plesk/api-examples/tree/master/python3

## Requirements
 | Name          | Link 
 |:--------------| :----
 | CertifyTheWeb | https://certifytheweb.com/
 | Python3 | https://www.python.org/downloads/windows/
 

## Install
 1. clone repo to your preferred Location
 2. Update start.bat  
    path to python.exe
    path to update_le.py
 3. Update update_le.py  
    host  
    login  
    password  
    log_filename  
 4. Add new Request to Certify Certificate Manager and set Authorization Settings
    | Setting            | Value                  | Note
    |:-------------------| :--------------------- | :----
    | Challenge Type     | dns-01                 |
    | DNS Update Methode | (Use Custom Script)    |
    | Dns Zone Id        | Site id from plesk     | Open the DNS Zone in Plesk. The ID is shown in the URL
    | Create Script Path | <path to update_le.py> |
    | Delete Script Path | <path to update_le.py> |
    | Propagatoin Delay  | 60                     | How many seconds to wait to check DNS after creating the _acme-challenge record

## ToDo
 - Test Renew as the script has not yet renewn a cert
 - start.bat  
   paths as variables
 - update_le.py  
   pass host, login, password and log_filename from start.bat
 - log rotation monthly