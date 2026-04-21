import requests

def debug_zs():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://api2.sota.org.uk/api/associations/ZS"
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Regions for ZS: {data.get('regions', [])}")

if __name__ == "__main__":
    debug_zs()
