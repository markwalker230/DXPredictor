import requests

def test_sota_api2_regions():
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Try regions endpoint
    url = "https://api2.sota.org.uk/api/regions/ZS/GA"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Data found for ZS/GA: {len(data.get('summits', []))}")
            if data.get('summits'): print(f"Sample summit: {data['summits'][0]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_sota_api2_regions()
