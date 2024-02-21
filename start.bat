REM This script would be called with the parameters <target domain> <record name> <record value> <zone id (optionally)>
REM this example then calls a custom python script forwarding all the arguments

"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe" C:\Service\Scripts\LE\update_le.py %*