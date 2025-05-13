# Sorun Giderme Kılavuzu

Bu belge, The Dyrt Scraper uygulamasını çalıştırırken karşılaşabileceğiniz yaygın sorunları ve çözümlerini içerir.

## Veritabanı Bağlantı Sorunları

### Hata: "could not translate host name 'postgres' to address: No such host is known"

Bu hata, uygulamanın "postgres" adlı bir host'a bağlanmaya çalıştığını ancak bu host'u bulamadığını gösterir. Bu genellikle Docker konteynerlerini başlatmadan doğrudan Python kodunu çalıştırdığınızda oluşur.

**Çözüm:**

1. Docker kullanıyorsanız:
   - Docker konteynerlerinin çalıştığından emin olun:
     ```
     docker-compose ps
     ```
   - Eğer çalışmıyorsa, başlatın:
     ```
     docker-compose up -d
     ```

2. Yerel geliştirme için:
   - Yerel çalıştırma scriptlerini kullanın:
     ```
     # Windows
     run_local.bat --scrape
     
     # Unix/Linux/macOS
     ./run_local.sh --scrape
     ```
   - Bu scriptler, DOCKER_ENV değişkenini "false" olarak ayarlayarak yerel veritabanı bağlantısını kullanır.

### Hata: "FATAL: password authentication failed for user 'user'"

Bu hata, veritabanı kullanıcı adı veya şifresinin yanlış olduğunu gösterir.

**Çözüm:**

1. `.env` dosyasındaki veritabanı bağlantı bilgilerini kontrol edin.
2. PostgreSQL'de doğru kullanıcının oluşturulduğundan emin olun:
   ```
   psql -U postgres -c "SELECT usename FROM pg_user;"
   ```
3. Gerekirse, kullanıcıyı yeniden oluşturun:
   ```
   psql -U postgres -c "CREATE USER \"user\" WITH PASSWORD 'password';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE case_study TO \"user\";"
   ```

## API Sorunları

### Hata: "404 Client Error: Not Found for url: https://thedyrt.com/api/v6/campgrounds/search"

Bu hata, The Dyrt API'sine yapılan isteklerin 404 Not Found hatası döndürdüğünü gösterir. Bu, API endpoint'inin değişmiş olabileceği anlamına gelir.

**Çözüm:**

1. API endpoint'ini güncelleyin:
   - The Dyrt web sitesinin ağ trafiğını analiz ederek güncel API endpoint'ini bulun.
   - `src/scraper.py` dosyasındaki `SEARCH_API_URL` değişkenini güncelleyin.
   - Tarayıcının geliştirici araçlarını kullanarak ağ trafiğını izleyin ve doğru API endpoint'ini bulun.

2. HTTP başlıklarını güncelleyin:
   - The Dyrt web sitesi, belirli HTTP başlıkları gerektiriyor olabilir.
   - `src/scraper.py` dosyasındaki `headers` değişkenini güncelleyin.

3. API istek formatını güncelleyin:
   - The Dyrt web sitesi, API istek formatını değiştirmiş olabilir.
   - Örneğin, yeni format şöyle olabilir:
     ```
     https://thedyrt.com/api/search?filters={"bbox":"-85.563,34.71,-69.537,42.095"}
     ```
   - `src/scraper.py` dosyasındaki `search_campgrounds` metodunu güncelleyin.

### Hata: "Address already in use"

Bu hata, API sunucusunun bağlanmaya çalıştığı port'un zaten kullanımda olduğunu gösterir.

**Çözüm:**

Farklı bir port numarası belirtin:
```
python main.py --api --port 8001
```

## Scraper Sorunları

### Hata: "Connection refused" veya "Timeout"

Bu hatalar, The Dyrt API'sine bağlanırken sorun yaşandığını gösterir.

**Çözüm:**

1. İnternet bağlantınızı kontrol edin.
2. The Dyrt web sitesinin erişilebilir olduğundan emin olun.
3. Scraper'ı daha düşük bir hızda çalıştırmayı deneyin (bölge sayısını azaltın veya istekler arasındaki bekleme süresini artırın).

### Hata: "Validation error for campground"

Bu hata, API'den alınan verilerin Pydantic modeline uymadığını gösterir.

**Çözüm:**

1. Hata mesajını kontrol ederek hangi alanın sorun yarattığını belirleyin.
2. Gerekirse, Pydantic modelini güncelleyin veya veri dönüşümü ekleyin.

## Zamanlayıcı Sorunları

### Hata: "Scheduler stopped unexpectedly"

Bu hata, zamanlayıcının beklenmedik bir şekilde durduğunu gösterir.

**Çözüm:**

1. Log dosyalarını kontrol ederek hatanın nedenini belirleyin.
2. Gerekirse, zamanlayıcıyı daha kısa aralıklarla çalıştırın.
3. Sistem kaynaklarının yeterli olduğundan emin olun.