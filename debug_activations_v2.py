import requests
import maidenhead
import json

def test_new_endpoints(gs):
    lat, lon = maidenhead.to_location(gs)
    print(f"--- DIAGNOSTICS FOR {gs} (Lat: {lat:.2f}, Lon: {lon:.2f}) ---\n")
    
    # 1. New SOTA Endpoint (SOTLAS/API2)
    sota_url = f"https://api2.sota.org.uk/api/summits/nearby?lat={lat}&lon={lon}&radius=50"
    print(f"SOTA Query: {sota_url}")
    try:
        r = requests.get(sota_url, timeout=15)
        print(f"SOTA Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"SOTA Found: {len(data)} results")
            print(json.dumps(data[:2], indent=2)) # Show first 2
        else:
            print(f"SOTA Error: {r.text[:200]}")
    except Exception as e:
        print(f"SOTA Exception: {e}")

    # 2. New POTA Stats Endpoint
    pota_url = f"https://api.pota.app/stats/park/gridsquare/{gs}"
    print(f"\nPOTA Query: {pota_url}")
    try:
        r = requests.get(pota_url, timeout=15)
        print(f"POTA Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"POTA Found: {len(data)} results")
            print(json.dumps(data[:2], indent=2)) # Show first 2
        else:
            print(f"POTA Error: {r.text[:200]}")
    except Exception as e:
        print(f"POTA Exception: {e}")

if __name__ == "__main__":
    test_new_endpoints("KG33WW")
