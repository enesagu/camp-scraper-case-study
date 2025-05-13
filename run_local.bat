@echo off
REM Bu script, scraper'ı yerel ortamda çalıştırır

REM Gerekli ortam değişkenlerini ayarla
set DOCKER_ENV=false

REM Parametreleri kontrol et
if "%1"=="--scrape" (
    echo Running scraper locally...
    python main.py --scrape
) else if "%1"=="--schedule" (
    echo Running scheduler locally with interval %2 hours...
    python main.py --schedule %2
) else if "%1"=="--api" (
    echo Running API server locally on port %2...
    python main.py --api --port %2
) else (
    echo Usage:
    echo   run_local.bat --scrape
    echo   run_local.bat --schedule [hours]
    echo   run_local.bat --api [port]
)