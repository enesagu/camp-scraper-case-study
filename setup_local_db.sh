#!/bin/bash

echo "Setting up local PostgreSQL database for development..."

# PostgreSQL'i başlat (eğer zaten çalışmıyorsa)
echo "Checking if PostgreSQL is running..."
if ! pgrep -x "postgres" > /dev/null; then
    echo "Starting PostgreSQL service..."
    if [ -f /etc/init.d/postgresql ]; then
        sudo /etc/init.d/postgresql start
    elif [ -f /usr/local/bin/pg_ctl ]; then
        pg_ctl -D /usr/local/var/postgres start
    else
        echo "Could not find PostgreSQL service. Please start it manually."
    fi
else
    echo "PostgreSQL is already running."
fi

# Veritabanını oluştur
echo "Creating database..."
psql -U postgres -c "CREATE DATABASE case_study;"
psql -U postgres -c "CREATE USER \"user\" WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE case_study TO \"user\";"

# Tabloları oluştur
echo "Setting up database tables..."
python src/database_setup.py

echo "Setup completed!"