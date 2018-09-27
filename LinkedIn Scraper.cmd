cd /d %~dp0
pip install -r requirements.txt
python Main.py 
ping 127.0.0.1 -n 100 > nul