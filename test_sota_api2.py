import requests
import json

def test_sota_api2():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Test 1: Summits by association
    print("--- SOTA api2: Summits by association (ZS) ---")
    url = "https://api2.sota.org.uk/api/summits/ZS"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Summits found: {len(data)}")
            if data: print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"Exception: {e}")

    # Test 2: List of associations
    print("\n--- SOTA api2: List of associations ---")
    url = "https://api2.sota.org.uk/api/associations"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Associations found: {len(data)}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_sota_api2()
