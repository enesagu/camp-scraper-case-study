#!/bin/bash
# Bu script, scraper'ı yerel ortamda çalıştırır

# Gerekli ortam değişkenlerini ayarla
export DOCKER_ENV=false

# Parametreleri kontrol et
if [ "$1" == "--scrape" ]; then
    echo "Running scraper locally..."
    python main.py --scrape
elif [ "$1" == "--schedule" ]; then
    echo "Running scheduler locally with interval $2 hours..."
    python main.py --schedule $2
elif [ "$1" == "--api" ]; then
    echo "Running API server locally on port $2..."
    python main.py --api --port $2
else
    echo "Usage:"
    echo "  ./run_local.sh --scrape"
    echo "  ./run_local.sh --schedule [hours]"
    echo "  ./run_local.sh --api [port]"
fi