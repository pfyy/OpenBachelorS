call venv\Scripts\activate.bat
python -m flask --app src/app --debug run -h 127.0.0.1 -p 8443
pause
