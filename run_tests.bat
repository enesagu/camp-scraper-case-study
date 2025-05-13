@echo off
REM Bu script, The Dyrt scraper'ı test etmek için kullanılır

echo ===== The Dyrt Scraper Test Suite =====

REM Veritabanı bağlantısını test et
echo.
echo Testing database connection...
python test_db.py
if %ERRORLEVEL% NEQ 0 (
    echo Database test failed!
    exit /b %ERRORLEVEL%
)

REM API sunucusunu başlat (arka planda)
echo.
echo Starting API server...
start /b python main.py --api --port 8000
echo Waiting for API server to start...
timeout /t 5 /nobreak > nul

REM API endpoint'lerini test et
echo.
echo Testing API endpoints...
python test_api.py
if %ERRORLEVEL% NEQ 0 (
    echo API test failed!
    taskkill /f /im python.exe /fi "WINDOWTITLE eq python main.py --api --port 8000"
    exit /b %ERRORLEVEL%
)

REM API sunucusunu durdur
echo.
echo Stopping API server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq python main.py --api --port 8000"

echo.
echo All tests completed successfully!