$ErrorActionPreference = "Stop"
pyinstaller src\win_binary\main.py
Copy-Item -Path "conf", "data", "res", "aria2c.exe" -Destination "dist\main" -Recurse
