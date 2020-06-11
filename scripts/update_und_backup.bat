@echo off
REM
REM Backup der Datenbank und Update inklusive Datenbank Migraton ausführen
REM
set DATENBANK=db.sqlite3
set DATENBANK_BACKUP_DIR=db_backup
set SOURCE_DIR=src
set GIT_HOME=

REM * Backup Datenbank Datei
REM - Datum und Zeit ermitteln (https://superuser.com/a/720402)
for /f "tokens=2 delims==" %%G in ('wmic os get localdatetime /value') do set datetime=%%G
set JAHR=%datetime:~0,4%
set MONAT=%datetime:~4,2%
set TAG=%datetime:~6,2%
if not exist "%DATENBANK_BACKUP_DIR%" mkdir "%DATENBANK_BACKUP_DIR%"
cp "%DATENBANK%" "%DATENBANK_BACKUP_DIR%\%DATENBANK%_%JAHR%%MONAT%%TAG%"

REM * Update Source Dateien
IF DEFINED GIT_HOME (
cd %SOURCE_DIR%
%GIT_HOME%\bin\git pull
%GIT_HOME%\bin\git log --oneline -n1 > ../update_1.log
cd ..
)

REM Start Django Migraton
python38\python.exe src\manage.py migrate

echo "Update fertig"
pause
