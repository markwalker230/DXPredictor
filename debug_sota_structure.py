import requests
import json

def debug_sota_summits():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://api2.sota.org.uk/api/regions/ZS/GP"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        summits = data.get('summits', [])
        print(f"Summits in GP: {len(summits)}")
        if summits:
            print("First Summit Keys:", summits[0].keys())
            print("First Summit Sample:", summits[0])

if __name__ == "__main__":
    debug_sota_summits()
