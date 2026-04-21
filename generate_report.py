import json
import urllib.request
import math
import datetime

def gs_to_latlon(gs):
    """Pure Python Maidenhead to Lat/Lon conversion."""
    gs = gs.upper()
    if len(gs) < 4: return None, None
    
    lon = (ord(gs[0]) - ord('A')) * 20 - 180
    lat = (ord(gs[1]) - ord('A')) * 10 - 90
    lon += (ord(gs[2]) - ord('0')) * 2
    lat += (ord(gs[3]) - ord('0')) * 1
    
    if len(gs) >= 6:
        lon += (ord(gs[4].upper()) - ord('A')) * (2/24)
        lat += (ord(gs[5].upper()) - ord('A')) * (1/24)
        
    return lat, lon

def get_solar_data():
    """Fetch solar data using urllib."""
    try:
        # NOAA SFI/SSN
        with urllib.request.urlopen("https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json") as url:
            data = json.loads(url.read().decode())
            latest = data[-1]
            sfi = latest.get('smoothed_f10_7', 145)
            ssn = latest.get('smoothed_ssn', 90)
        
        # NOAA Kp
        with urllib.request.urlopen("https://services.swpc.noaa.gov/json/planetary_k_index_1m.json") as url:
            kp_data = json.loads(url.read().decode())
            kp = kp_data[-1].get('kp_index', 2)
            
        return {"sfi": sfi, "ssn": ssn, "kp": kp}
    except Exception as e:
        return {"sfi": 150, "ssn": 100, "kp": 2, "error": str(e)}

def calculate_prop(hour_utc, band, lat, lon, sfi, kp, power_w, ant_gain):
    # Solar local time approx
    local_time = (hour_utc + (lon / 15.0)) % 24
    
    if band == 10:
        mu, sigma = 12.5, 3.0
        base = math.exp(-((local_time - mu)**2) / (2 * sigma**2))
        factor = max(0, min(1.2, (sfi - 60) / 100.0))
    elif band == 20:
        mu, sigma = 14.0, 5.0
        base = 0.3 + 0.7 * math.exp(-((local_time - mu)**2) / (2 * sigma**2))
        factor = max(0, min(1.1, (sfi - 60) / 80.0))
    else: # 40m
        base = 0.2 + 0.8 * (1 - math.exp(-((local_time - 12)**2) / (2 * 4.0**2)))
        factor = 1.0
        
    db_rel = 10 * math.log10(power_w / 5.0) + (ant_gain - 2.15)
    p_factor = 1.0 + (db_rel / 20.0)
    kp_penalty = 1.0 - (min(kp, 9) * 0.1)
    
    return max(0, min(1.0, base * factor * p_factor * kp_penalty))

def generate_html(gs, power_label, ant_label, power_w, ant_gain):
    lat, lon = gs_to_latlon(gs)
    solar = get_solar_data()
    
    bands = [10, 20, 40]
    results = []
    for h in range(24):
        row = {"utc": h, "local": (h+2)%24}
        for b in bands:
            row[f"b{b}"] = calculate_prop(h, b, lat, lon, solar['sfi'], solar['kp'], power_w, ant_gain)
        results.append(row)

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DX Predictor - {gs}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f8f9fa; font-family: sans-serif; padding: 20px; }}
            .card {{ margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .metric {{ font-size: 24px; font-weight: bold; color: #0d6efd; }}
            .band-10 {{ color: #FF5733; }} .band-20 {{ color: #33FF57; }} .band-40 {{ color: #3357FF; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-4">📡 HF DX Propagation Predictor</h1>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="card p-3">
                        <h5>Station Config</h5>
                        <p>Gridsquare: <strong>{gs}</strong><br>
                        Power: {power_label} ({power_w}W)<br>
                        Antenna: {ant_label}</p>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card p-3">
                        <h5>Live Solar Weather (NOAA)</h5>
                        <div class="row text-center">
                            <div class="col">SFI<br><span class="metric">{solar['sfi']}</span></div>
                            <div class="col">SSN<br><span class="metric">{int(solar['ssn'])}</span></div>
                            <div class="col">Kp-Index<br><span class="metric">{solar['kp']}</span></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card p-3">
                <div id="chart"></div>
            </div>

            <div class="card p-3">
                <h5>Detailed Propagation Table (UTC and UTC+2)</h5>
                <div class="table-responsive">
                    <table class="table table-sm table-hover text-center">
                        <thead>
                            <tr><th>UTC</th><th>Local</th><th>10m</th><th>20m</th><th>40m</th></tr>
                        </thead>
                        <tbody id="table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const data = {json.dumps(results)};
            const trace10 = {{ x: data.map(d => d.utc), y: data.map(d => d.b10), name: '10m', type: 'scatter', line: {{shape: 'spline'}} }};
            const trace20 = {{ x: data.map(d => d.utc), y: data.map(d => d.b20), name: '20m', type: 'scatter', line: {{shape: 'spline'}} }};
            const trace40 = {{ x: data.map(d => d.utc), y: data.map(d => d.b40), name: '40m', type: 'scatter', line: {{shape: 'spline'}} }};
            
            Plotly.newPlot('chart', [trace10, trace20, trace40], {{
                title: 'Propagation Probability Over 24 Hours',
                xaxis: {{ title: 'Hour (UTC)', dtick: 2 }},
                yaxis: {{ title: 'Probability', range: [0, 1.1] }}
            }});

            const tbody = document.getElementById('table-body');
            data.forEach(d => {{
                const row = `<tr>
                    <td>${{d.utc}}:00</td>
                    <td>${{d.local}}:00</td>
                    <td style="background: rgba(0,255,0,${{d.b10}})">${{d.b10.toFixed(2)}}</td>
                    <td style="background: rgba(0,255,0,${{d.b20}})">${{d.b20.toFixed(2)}}</td>
                    <td style="background: rgba(0,255,0,${{d.b40}})">${{d.b40.toFixed(2)}}</td>
                </tr>`;
                tbody.innerHTML += row;
            }});
        </script>
    </body>
    </html>
    """
    with open("dx_report.html", "w") as f:
        f.write(html_template)
    print("\n✅ Report generated successfully: dx_report.html")
    print("Open 'dx_report.html' in your browser to see the results.")

if __name__ == "__main__":
    print("--- DX Predictor CLI ---")
    gs = input("Enter Maidenhead Gridsquare [KG33ww]: ") or "KG33ww"
    p_choice = input("Power: 1 for <20W, 2 for 100W [1]: ") or "1"
    pw = 15 if p_choice == "1" else 100
    pl = "Low Power" if p_choice == "1" else "High Power"
    
    generate_html(gs.upper(), pl, "Standard Antenna", pw, 2.15)
