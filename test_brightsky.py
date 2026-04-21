import requests
import json

def test_brightsky():
    # BrightSky (DWD based, excellent API)
    lat, lon = -26.08, 27.83
    url = f"https://api.brightsky.dev/weather?lat={lat}&lon={lon}&date={datetime.datetime.now().isoformat()}"
    # Wait, brightsky usually expects a date range for forecast.
    # Let's try current:
    url = f"https://api.brightsky.dev/current_weather?lat={lat}&lon={lon}"
    try:
        r = requests.get(url, timeout=10)
        print(f"BrightSky Status: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    import datetime
    test_brightsky()
