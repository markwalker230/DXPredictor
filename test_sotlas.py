import requests

def test_sotlas():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://api.sotl.as/summits/nearby?lat=-26.08&lon=27.83&radius=50"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Results: {len(r.json())}")
            if r.json(): print(f"Sample: {r.json()[0]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_sotlas()
