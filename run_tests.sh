#!/bin/bash
# Bu script, The Dyrt scraper'ı test etmek için kullanılır

echo "===== The Dyrt Scraper Test Suite ====="

# Veritabanı bağlantısını test et
echo -e "\nTesting database connection..."
python test_db.py
if [ $? -ne 0 ]; then
    echo "Database test failed!"
    exit 1
fi

# API sunucusunu başlat (arka planda)
echo -e "\nStarting API server..."
python main.py --api --port 8000 &
API_PID=$!
echo "Waiting for API server to start..."
sleep 5

# API endpoint'lerini test et
echo -e "\nTesting API endpoints..."
python test_api.py
if [ $? -ne 0 ]; then
    echo "API test failed!"
    kill $API_PID
    exit 1
fi

# API sunucusunu durdur
echo -e "\nStopping API server..."
kill $API_PID

echo -e "\nAll tests completed successfully!"