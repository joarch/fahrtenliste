start python38\python.exe src\manage.py runserver

timeout 2

start cmd /c "python38\python.exe -m webbrowser -t http://127.0.0.1:8000"  && exit 0

