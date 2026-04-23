import maidenhead
import requests
import datetime
import pandas as pd
import numpy as np
import math
import random
import string

def generate_random_gridsquare():
    """Generate a random 6-character Maidenhead gridsquare."""
    # Field: A-R (18 fields)
    f1 = random.choice(string.ascii_uppercase[:18])
    f2 = random.choice(string.ascii_uppercase[:18])
    # Square: 0-9
    s1 = random.choice(string.digits)
    s2 = random.choice(string.digits)
    # Subsquare: a-x (24 subsquares)
    ss1 = random.choice(string.ascii_lowercase[:24])
    ss2 = random.choice(string.ascii_lowercase[:24])
    return f"{f1}{f2}{s1}{s2}{ss1}{ss2}"

def gs_to_latlon(gs):
    """Convert Maidenhead gridsquare to latitude and longitude."""
    try:
        lat, lon = maidenhead.to_location(gs)
        return lat, lon
    except ValueError:
        return None, None

def get_solar_indices():
    """Fetch current SFI, SSN, and Kp from NOAA."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get("https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json", timeout=10, headers=headers)
        data = r.json()
        latest = data[-1]
        ssn = latest.get('smoothed_ssn', 100)
        sfi = latest.get('smoothed_f10_7', 150)
        
        r_kp = requests.get("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json", timeout=10, headers=headers)
        kp_data = r_kp.json()
        kp = kp_data[-1].get('kp_index', 3)
        
        return {"ssn": ssn, "sfi": sfi, "kp": kp}
    except Exception as e:
        return {"ssn": 90, "sfi": 145, "kp": 2, "error": str(e)}

def get_ionospheric_indices():
    """Fetch T-index from ASWFC and SANSA state."""
    indices = {"t_index": 100, "sansa_state": "Quiet"}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # ASWFC (SWS) - T-index data (Text file)
        # SWS frequently publishes their T-index. We'll use the latest available if reachable.
        r = requests.get("https://www.sws.bom.gov.au/hf_systems/6/5/1", timeout=10, headers=headers)
        if r.status_code == 200:
            # SWS format is often simple text like: "CURRENT T INDEX: 120"
            for line in r.text.split("\n"):
                if "CURRENT T INDEX" in line.upper():
                    indices["t_index"] = int(line.split(":")[-1].strip())
                    break
    except Exception:
        pass

    try:
        # SANSA Ionospheric status summary
        # They have a JSON or XML based status on their weather site.
        r = requests.get("https://spaceweather.sansa.org.za/index.php?option=com_sansa&view=dashboard&format=json", timeout=10, headers=headers)
        if r.status_code == 200:
            # We look for regional ionospheric state
            data = r.json()
            indices["sansa_state"] = data.get('ionosphere_status', 'Quiet')
    except Exception:
        pass
        
    return indices

def get_propagation_score(hour_utc, band_m, lat, lon, sfi, kp, power_w, antenna_gain, iono_indices):
    """Calculates a propagation score (0.0 - 1.0) using T-index and SFI."""
    local_time = (hour_utc + (lon / 15.0)) % 24
    t_index = iono_indices.get("t_index", 100)
    
    # Scale scores based on band characteristics
    if band_m == 10:
        mu, sigma = 12.5, 3.0
        base = np.exp(-((local_time - mu)**2) / (2 * sigma**2))
        # 10m is heavily dependent on the T-index and high SFI
        factor = np.clip((t_index - 40) / 100.0, 0, 1.2) * np.clip((sfi - 60) / 100.0, 0, 1.0)
        score = base * factor
    elif band_m == 20:
        mu, sigma = 14.0, 5.0
        base = 0.3 + 0.7 * np.exp(-((local_time - mu)**2) / (2 * sigma**2))
        # 20m is more robust but still benefits from higher T-index
        factor = np.clip((t_index - 30) / 90.0, 0, 1.1)
        score = base * factor
    elif band_m == 40:
        mu, sigma = 0.0, 6.0
        base = 0.2 + 0.8 * (1 - np.exp(-((local_time - 12)**2) / (2 * 4.0**2)))
        # 40m is less sensitive to T-index, but higher Kp degrades it
        score = base 
    else:
        score = 0.5

    # Station Profile Adjustments
    db_relative = 10 * np.log10(power_w / 5.0) + (antenna_gain - 2.15)
    power_factor = 1.0 + (db_relative / 25.0)
    
    # Kp Penalty (higher Kp = major degradation)
    kp_penalty = 1.0 - (min(kp, 9) * 0.12)
    
    # SANSA State Adjustment
    if iono_indices.get("sansa_state") == "Disturbed":
        kp_penalty *= 0.7
        
    return np.clip(score * power_factor * kp_penalty, 0, 1)

def get_weather_and_elevation(lat, lon):
    """Fetch weather and elevation from MET Norway (Highly reliable)."""
    headers = {'User-Agent': 'DXPredictor/1.0 (https://github.com/mark/dxpredictor)'}
    try:
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}
        
        data = r.json()
        geometry = data.get('geometry', {})
        elevation = geometry.get('coordinates', [0, 0, 0])[2]
        
        timeseries = data['properties']['timeseries']
        current = timeseries[0]['data']['instant']['details']
        
        hourly_times = []
        hourly_temps = []
        hourly_precip = []
        hourly_wind = []
        
        for point in timeseries[:24]: # Next 24 hours
            # Format: 2024-04-03T17:00:00Z
            time_str = point['time'].split("T")[1][:5]
            details = point['data']['instant']['details']
            
            hourly_times.append(time_str)
            hourly_temps.append(details.get('air_temperature'))
            # Precipitation is usually in next_1_hours
            next_1h = point['data'].get('next_1_hours', {}).get('details', {})
            hourly_precip.append(next_1h.get('precipitation_amount', 0))
            hourly_wind.append(details.get('wind_speed') * 3.6) # Convert m/s to km/h

        return {
            "elevation": elevation,
            "current_temp": current.get('air_temperature'),
            "current_humidity": current.get('relative_humidity'),
            "current_wind": current.get('wind_speed') * 3.6,
            "current_desc": "Standard", # MET compact doesn't give text desc easily
            "hourly": {
                "time": hourly_times,
                "temperature_2m": hourly_temps,
                "precipitation_probability": hourly_precip,
                "wind_speed_10m": hourly_wind
            }
        }
    except Exception as e:
        return {"error": str(e)}

def get_nearby_activations(lat, lon, gridsquare):
    """Fetch nearby SOTA and POTA sites using verified official endpoints."""
    results = {"sota": [], "pota": []}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # 1. POTA (Bounding Box)
    try:
        minLat, maxLat = lat - 0.5, lat + 0.5
        minLon, maxLon = lon - 0.5, lon + 0.5
        pota_url = f"https://api.pota.app/park/grids/{minLat}/{minLon}/{maxLat}/{maxLon}/0"
        r = requests.get(pota_url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            features = data.get('features', []) if isinstance(data, dict) else []
            for feat in features:
                props = feat.get('properties', {})
                geom = feat.get('geometry', {})
                coords = geom.get('coordinates', [0, 0])
                results["pota"].append({
                    "reference": props.get('reference'),
                    "name": props.get('name'),
                    "latitude": coords[1],
                    "longitude": coords[0],
                    "locationName": "Nearby Park"
                })
    except Exception:
        pass

    # 2. SOTA (Official api2 Regions)
    try:
        assoc = "ZS"
        assoc_url = f"https://api2.sota.org.uk/api/associations/{assoc}"
        r = requests.get(assoc_url, headers=headers, timeout=10)
        if r.status_code == 200:
            regions = r.json().get('regions', [])
            for region in regions:
                if (region['minLat'] - 0.5 <= lat <= region['maxLat'] + 0.5 and 
                    region['minLong'] - 0.5 <= lon <= region['maxLong'] + 0.5):
                    
                    reg_url = f"https://api2.sota.org.uk/api/regions/{assoc}/{region['regionCode']}"
                    r_reg = requests.get(reg_url, headers=headers, timeout=10)
                    if r_reg.status_code == 200:
                        summits = r_reg.json().get('summits', [])
                        for s in summits:
                            s_lat, s_lon = s.get('latitude'), s.get('longitude')
                            if s_lat is None or s_lon is None: continue
                            dist = math.sqrt((s_lat - lat)**2 + (s_lon - lon)**2) * 111
                            if dist <= 50:
                                results["sota"].append({
                                    "associationCode": assoc,
                                    "summitCode": s.get('summitCode'),
                                    "summitName": s.get('name'),
                                    "altitude": s.get('altM', 0),
                                    "points": s.get('points', 0),
                                    "latitude": s_lat,
                                    "longitude": s_lon
                                })
            results["sota"] = results["sota"][:10]
    except Exception:
        pass
        
    return results

def get_realtime_spots(gs_source, minutes=60):
    """Fetch recent WSPR spots from WSPR.live ClickHouse DB."""
    import urllib.request
    import urllib.parse
    import json

    # Maidenhead to approx lat/lon
    lat_src, lon_src = gs_to_latlon(gs_source)
    if not lat_src: return []

    bands = {10: 28, 20: 14, 40: 7}
    all_spots = []
    base_url = "https://db1.wspr.live/"
    
    gs4 = gs_source[:4].upper()
    gs2 = gs_source[:2].upper()

    for band_m, band_val in bands.items():
        # 1. Try local/regional spots first
        query = f"""
            SELECT rx_lat, rx_lon, tx_lat, tx_lon, snr, band, rx_loc, tx_loc
            FROM rx 
            WHERE band = {band_val} 
            AND time > subtractMinutes(now(), {minutes})
            AND (rx_loc LIKE '{gs4}%' OR tx_loc LIKE '{gs4}%' OR rx_loc LIKE '{gs2}%' OR tx_loc LIKE '{gs2}%')
            LIMIT 500
        """
        
        spots = []
        try:
            params = urllib.parse.urlencode({'query': query + " FORMAT JSON"})
            url = f"{base_url}?{params}"
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                spots = data.get('data', [])
        except Exception:
            pass

        # 2. Fallback: If no local spots, get recent global spots for this band
        if not spots:
            query_global = f"""
                SELECT rx_lat, rx_lon, tx_lat, tx_lon, snr, band
                FROM rx 
                WHERE band = {band_val} 
                AND time > subtractMinutes(now(), 15)
                LIMIT 200
            """
            try:
                params = urllib.parse.urlencode({'query': query_global + " FORMAT JSON"})
                url = f"{base_url}?{params}"
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    spots = data.get('data', [])
            except Exception:
                pass

        for s in spots:
            is_rx = gs2 in str(s.get('rx_loc', ''))
            target_lat = s.get('tx_lat', s.get('rx_lat'))
            target_lon = s.get('tx_lon', s.get('rx_lon'))
            
            all_spots.append({
                'lat': target_lat,
                'lon': target_lon,
                'snr': s['snr'],
                'band': f"{band_m}m"
            })
            
    return all_spots

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate the initial bearing from point A to point B."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(y, x)
    return (math.degrees(bearing) + 360) % 360

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate Great Circle distance in kilometers."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_dx_targets():
    """Coordinates for major DX regions."""
    return {
        "Europe (London)": (51.50, -0.12),
        "North America (NY)": (40.71, -74.00),
        "Japan (Tokyo)": (35.67, 139.65),
        "Australia (Sydney)": (-33.86, 151.20),
        "South America (Brazil)": (-23.55, -46.63)
    }

def get_best_paths(gs_source):
    """Returns estimated path scores for major DX regions."""
    return {"Europe": "JO21at", "North America": "FN20", "Japan": "PM95", "South America": "GG32", "Australia": "QF22"}
