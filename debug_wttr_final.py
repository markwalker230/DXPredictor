import requests
import json

def debug_weather_wttr():
    lat, lon = -26.08, 27.83
    url = f"https://wttr.in/{lat},{lon}?format=j1"
    try:
        r = requests.get(url, timeout=15)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Current Condition Keys:", data.get('current_condition', [{}])[0].keys())
            print("Weather Keys:", data.get('weather', [{}])[0].keys())
            hourly = data.get('weather', [{}])[0].get('hourly', [])
            print(f"Hourly count (Day 1): {len(hourly)}")
            if hourly:
                print("First hourly point sample:", hourly[0])
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_weather_wttr()
