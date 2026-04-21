import requests

def test_sota_region():
    headers = {'User-Agent': 'Mozilla/5.0'}
    # ZS/GA is Gauteng (Johannesburg area)
    url = "https://api2.sota.org.uk/api/summits/ZS/GA"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Summits in ZS/GA: {len(data)}")
            if data: print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_sota_region()
