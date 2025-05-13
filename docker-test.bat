@echo off
REM Bu script, Docker ortamında The Dyrt scraper'ı test etmek için kullanılır

echo ===== The Dyrt Scraper Docker Test Suite =====

REM Docker konteynerlerini başlat
echo.
echo Starting Docker containers...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start Docker containers!
    exit /b %ERRORLEVEL%
)

REM Veritabanı tablolarını oluştur
echo.
echo Initializing database...
docker-compose run scraper python -c "from src.database import init_db; init_db()"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to initialize database!
    docker-compose down
    exit /b %ERRORLEVEL%
)

REM Scraper'ı çalıştır
echo.
echo Running scraper...
docker-compose run scraper python main.py --scrape
if %ERRORLEVEL% NEQ 0 (
    echo Scraper failed!
    docker-compose down
    exit /b %ERRORLEVEL%
)

REM API sunucusunu başlat
echo.
echo Starting API server...
docker-compose run -d -p 8000:8000 scraper python main.py --api
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start API server!
    docker-compose down
    exit /b %ERRORLEVEL%
)

echo Waiting for API server to start...
timeout /t 5 /nobreak > nul

REM API endpoint'lerini test et
echo.
echo Testing API endpoints...
python test_api.py
if %ERRORLEVEL% NEQ 0 (
    echo API test failed!
    docker-compose down
    exit /b %ERRORLEVEL%
)

REM Veritabanını test et
echo.
echo Testing database...
docker-compose exec postgres psql -U user -d case_study -c "SELECT COUNT(*) FROM campgrounds;"
if %ERRORLEVEL% NEQ 0 (
    echo Database test failed!
    docker-compose down
    exit /b %ERRORLEVEL%
)

REM Docker konteynerlerini durdur
echo.
echo Stopping Docker containers...
docker-compose down

echo.
echo All Docker tests completed successfully!