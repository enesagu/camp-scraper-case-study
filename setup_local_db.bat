@echo off
echo Setting up local PostgreSQL database for development...

REM PostgreSQL'i başlat (eğer zaten çalışmıyorsa)
echo Checking if PostgreSQL is running...
sc query postgresql-x64-13 | findstr "RUNNING"
if %ERRORLEVEL% NEQ 0 (
    echo Starting PostgreSQL service...
    net start postgresql-x64-13
) else (
    echo PostgreSQL is already running.
)

REM Veritabanını oluştur
echo Creating database...
psql -U postgres -c "CREATE DATABASE case_study;"
psql -U postgres -c "CREATE USER \"user\" WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE case_study TO \"user\";"

REM Tabloları oluştur
echo Setting up database tables...
python src/database_setup.py

echo Setup completed!