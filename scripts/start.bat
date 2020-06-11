GIT_HOME=

IF DEFINED GIT_HOME (
echo "" >> update_1.log
cd %SOURCE_DIR%
%GIT_HOME%\bin\git log --oneline -n1 > ../update_2.log
cd ..
fc update_1.log update_2.log
if errorlevel 1 goto UPDATE
)

goto START
:UPDATE
echo "Es steht ein neues Programm Update zur Verfügung:"
type update_2.log
echo "Das Update kann mit dem Update Skript eingespielt werden."
pause

:START

start python38\python.exe src\manage.py runserver

timeout 2

start cmd /c "python38\python.exe -m webbrowser -t http://127.0.0.1:8000"  && exit 0
