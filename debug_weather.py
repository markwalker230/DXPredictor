import requests
import json

def debug_weather():
    lat, lon = -26.08, 27.83
    print(f"Testing weather for Lat: {lat}, Lon: {lon}")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&hourly=temperature_2m,precipitation_probability,wind_speed_10m&timezone=auto&forecast_days=1"
    try:
        r = requests.get(url, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Keys in response:", data.keys())
            if 'current' in data:
                print("Current Weather:", data['current'])
            if 'hourly' in data:
                print("Hourly Keys:", data['hourly'].keys())
                print("Hourly Time Sample:", data['hourly']['time'][:3])
        else:
            print("Error Response:", r.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_weather()
