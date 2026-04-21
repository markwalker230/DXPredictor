import requests
import json
import maidenhead

def diagnostic(gs):
    lat, lon = maidenhead.to_location(gs)
    print(f"DIAGNOSTIC FOR {gs} (Lat: {lat}, Lon: {lon})\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 1. POTA GRIDS (Bounding Box)
    print("--- 1. POTA GRIDS (Bounding Box +/- 0.5 deg) ---")
    minLat, maxLat = lat - 0.5, lat + 0.5
    minLon, maxLon = lon - 0.5, lon + 0.5
    pota_url = f"https://api.pota.app/park/grids/{minLat}/{minLon}/{maxLat}/{maxLon}/0"
    print(f"URL: {pota_url}")
    try:
        r = requests.get(pota_url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # POTA grids returns a GeoJSON-like list or dict
            print(f"Data type: {type(data)}")
            if isinstance(data, list):
                print(f"Results: {len(data)}")
                if data: print(f"Sample: {data[0]}")
            elif isinstance(data, dict):
                features = data.get('features', [])
                print(f"Features: {len(features)}")
                if features: print(f"Sample: {features[0]}")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

    # 2. SOTA api2 (Association ZS)
    print("\n--- 2. SOTA api2 (Association ZS) ---")
    sota_url = "https://api2.sota.org.uk/api/associations/ZS"
    print(f"URL: {sota_url}")
    try:
        r = requests.get(sota_url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Regions found: {len(data.get('regions', []))}")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

    # 3. SOTA api-v1 (Nearby)
    print("\n--- 3. SOTA api-v1 (Nearby) ---")
    sota_url = f"https://api-v1.sota.org.uk/summits/nearby/{lat}/{lon}/50"
    print(f"URL: {sota_url}")
    try:
        r = requests.get(sota_url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Results: {len(data)}")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

    # 4. SOTALive API
    print("\n--- 4. SOTALive API ---")
    sota_url = f"https://www.sotalive.tk/api/sotasummits?lat={lat}&lon={lon}&range=50"
    print(f"URL: {sota_url}")
    try:
        r = requests.get(sota_url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Results: {len(data)}")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    diagnostic("KG33WW")
