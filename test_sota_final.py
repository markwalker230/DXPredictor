import requests

def test_sota_summits_final():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Try 1: Region summits
    print("--- Try 1: api2 /summits/ZS/GP ---")
    url = "https://api2.sota.org.uk/api/summits/ZS/GP"
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Found: {len(r.json())}")
        
    # Try 2: Regions endpoint (which might contain summits)
    print("\n--- Try 2: api2 /regions/ZS/GP ---")
    url = "https://api2.sota.org.uk/api/regions/ZS/GP"
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Summits in data: {len(data.get('summits', []))}")

    # Try 3: Association summits with region filter
    print("\n--- Try 3: api2 /summits?associationCode=ZS&regionCode=GP ---")
    url = "https://api2.sota.org.uk/api/summits?associationCode=ZS&regionCode=GP"
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Found: {len(r.json())}")

if __name__ == "__main__":
    test_sota_summits_final()
