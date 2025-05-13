import requests
import time

# Grid ayarları
lat_start, lat_end = 24.5, 49.5
lng_start, lng_end = -125, -66.9
step = 2.0  # Her adımda kaç derece ilerleyecek (kare boyutu)

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_bbox(west, south, east, north):
    url = "https://thedyrt.com/api/v6/locations/search-results"
    params = {
        "filter[search][drive_time]": "any",
        "filter[search][air_quality]": "any",
        "filter[search][electric_amperage]": "any",
        "filter[search][max_vehicle_length]": "any",
        "filter[search][price]": "any",
        "filter[search][rating]": "any",
        "filter[search][bbox]": f"{west},{south},{east},{north}",
        "sort": "recommended",
        "page[number]": 1,
        "page[size]": 500
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"⚠️ Hata {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"🚨 İstek hatası: {e}")
        return []

# Grid üzerinde dolaş
all_campgrounds = []
for lat in range(int(lat_start), int(lat_end), int(step)):
    for lng in range(int(lng_start), int(lng_end), int(step)):
        south = lat
        north = lat + step
        west = lng
        east = lng + step
        print(f"📍 Tarama: bbox=({west},{south},{east},{north})")
        results = fetch_bbox(west, south, east, north)
        print(f"→ {len(results)} sonuç bulundu.\n")
        all_campgrounds.extend(results)
        time.sleep(1)  # API'yi yormamak için

print(f"\n✅ Toplam kamp yeri: {len(all_campgrounds)}")
