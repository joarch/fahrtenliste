@echo off
REM
REM Start des Programmes
REM
for /f "delims=" %%x in (config.txt) do (set "%%x")

IF DEFINED GIT_HOME (
cd %SOURCE_DIR%
%GIT_HOME%\bin\git log --oneline -n1 > ../update_2.log
cd ..
fc update_1.log update_2.log
if errorlevel 1 goto UPDATE
)

goto START
:UPDATE
echo "**********************************************************"
echo "Es steht ein neues Programm Update zur Verfügung"
echo "---------------------------------------------------------"
echo "Details:"
type update_2.log
echo "---------------------------------------------------------"
echo "Das Update kann mit dem Update Skript eingespielt werden."
echo "*********************************************************"
pause

:START

start python38\python.exe src\manage.py runserver

timeout 2

start cmd /c "python38\python.exe -m webbrowser -t http://127.0.0.1:8000"  && exit 0
