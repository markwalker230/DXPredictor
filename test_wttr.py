import requests

def test_wttr():
    # wttr.in format: wttr.in/Lat,Lon?format=j1
    url = "https://wttr.in/-26.08,27.83?format=j1"
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Current Temp:", data['current_condition'][0]['temp_C'])
            print("Forecast Sample:", data['weather'][0]['hourly'][0]['tempC'])
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_wttr()
