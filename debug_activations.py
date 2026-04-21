import requests
import maidenhead

def test_activations(gs):
    lat, lon = maidenhead.to_location(gs)
    print(f"Testing for {gs} (Lat: {lat}, Lon: {lon})")
    
    # Test SOTA
    print("\n--- Testing SOTA ---")
    sota_url = f"https://api-v1.sota.org.uk/summits/nearby/{lat}/{lon}/50"
    try:
        r = requests.get(sota_url, timeout=10)
        print(f"SOTA Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"SOTA Found: {len(data)} summits")
            if data: print(f"First result: {data[0].get('summitName')}")
        else:
            print(f"SOTA Error Response: {r.text[:100]}")
    except Exception as e:
        print(f"SOTA Exception: {e}")

    # Test POTA
    print("\n--- Testing POTA ---")
    # POTA API actually uses /park/gridsquare/{gs} or /park/nearby
    pota_url = f"https://api.pota.app/park/gridsquare/{gs}"
    try:
        r = requests.get(pota_url, timeout=10)
        print(f"POTA Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"POTA Found: {len(data)} parks")
            if data: print(f"First result: {data[0].get('name')}")
        else:
            print(f"POTA Error Response: {r.text[:100]}")
    except Exception as e:
        print(f"POTA Exception: {e}")

if __name__ == "__main__":
    test_activations("KG33WW")
