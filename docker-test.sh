#!/bin/bash
# Bu script, Docker ortamında The Dyrt scraper'ı test etmek için kullanılır

echo "===== The Dyrt Scraper Docker Test Suite ====="

# Docker konteynerlerini başlat
echo -e "\nStarting Docker containers..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Failed to start Docker containers!"
    exit 1
fi

# Veritabanı tablolarını oluştur
echo -e "\nInitializing database..."
docker-compose run scraper python -c "from src.database import init_db; init_db()"
if [ $? -ne 0 ]; then
    echo "Failed to initialize database!"
    docker-compose down
    exit 1
fi

# Scraper'ı çalıştır
echo -e "\nRunning scraper..."
docker-compose run scraper python main.py --scrape
if [ $? -ne 0 ]; then
    echo "Scraper failed!"
    docker-compose down
    exit 1
fi

# API sunucusunu başlat
echo -e "\nStarting API server..."
docker-compose run -d -p 8000:8000 scraper python main.py --api
if [ $? -ne 0 ]; then
    echo "Failed to start API server!"
    docker-compose down
    exit 1
fi

echo "Waiting for API server to start..."
sleep 5

# API endpoint'lerini test et
echo -e "\nTesting API endpoints..."
python test_api.py
if [ $? -ne 0 ]; then
    echo "API test failed!"
    docker-compose down
    exit 1
fi

# Veritabanını test et
echo -e "\nTesting database..."
docker-compose exec postgres psql -U user -d case_study -c "SELECT COUNT(*) FROM campgrounds;"
if [ $? -ne 0 ]; then
    echo "Database test failed!"
    docker-compose down
    exit 1
fi

# Docker konteynerlerini durdur
echo -e "\nStopping Docker containers..."
docker-compose down

echo -e "\nAll Docker tests completed successfully!"