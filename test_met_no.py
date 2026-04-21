import requests

def test_met_no():
    # MET Norway requires a User-Agent
    headers = {'User-Agent': 'DXPredictor/1.0 (https://github.com/mark/dxpredictor)'}
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=-26.08&lon=27.83"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # Elevation is in the 'geometry' section
            print("Elevation:", data['geometry']['coordinates'][2])
            # Current humidity
            print("Humidity:", data['properties']['timeseries'][0]['data']['instant']['details']['relative_humidity'])
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_met_no()
