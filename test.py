import requests

# Örnek: ABD'nin belli bir bölgesi için lat/lng sınırları (NY civarı)
bounds = {
    "ne": {"lat": 42.88, "lng": -73.45},  # Kuzeydoğu
    "sw": {"lat": 40.48, "lng": -75.10},  # Güneybatı
}

# API endpoint (yukarıdaki URL yapısından alınmış)
url = "https://api.thedyrt.com/v6/campgrounds/search"

# Parametreler (örneğin The Dyrt bu yapıyı kullanıyor)
params = {
    "bounds[ne][lat]": bounds["ne"]["lat"],
    "bounds[ne][lng]": bounds["ne"]["lng"],
    "bounds[sw][lat]": bounds["sw"]["lat"],
    "bounds[sw][lng]": bounds["sw"]["lng"],
    "filters[bookable]": "false",  # veya true
    "per_page": 50,
    "page": 1
}

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"{len(data['data'])} kamp alanı bulundu.")
    for campground in data['data']:
        print(f"{campground['name']} - {campground.get('location', {}).get('coordinates')}")
else:
    print("Hata:", response.status_code, response.text)
