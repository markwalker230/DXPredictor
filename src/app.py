import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
from utils import (gs_to_latlon, get_solar_indices, get_propagation_score, 
                   get_weather_and_elevation, get_nearby_activations, 
                   get_ionospheric_indices, get_dx_targets, calculate_bearing, calculate_distance,
                   generate_random_gridsquare)
import datetime
import numpy as np

# Page Configuration
st.set_page_config(page_title="SOTA/POTA DX Predictor by ZS6MDX", layout="wide", initial_sidebar_state="expanded")

if 'default_gs' not in st.session_state:
    st.session_state.default_gs = generate_random_gridsquare().upper()

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetric"] { background-color: #1e293b !important; padding: 15px !important; border-radius: 10px !important; border: 2px solid #3b82f6 !important; box-shadow: 2px 2px 10px rgba(0,0,0,0.2) !important; margin-bottom: 10px !important; }
    div[data-testid="stMetricLabel"] { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { color: #60a5fa !important; font-weight: 800 !important; }
    div[data-testid="stMetricDelta"] { color: #f87171 !important; font-weight: bold !important; }
    .activation-card { background-color: #ffffff !important; color: #1e293b !important; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("📡 SOTA/ POTA HF DX Propagation & Path Forecast by ZS6MDX")
st.markdown("---")

# Sidebar - Settings
st.sidebar.header("Station Configuration")
gridsquare = st.sidebar.text_input("Home Maidenhead Gridsquare", value=st.session_state.default_gs).upper()

power_options = {"QRP (<20W)": 15, "Standard (100W)": 100, "QRO (1500W)": 1500}
power_label = st.sidebar.selectbox("Transmit Power Level", list(power_options.keys()))
power_w = power_options[power_label]

antenna_options = {"End-fed Half Wave (EFHW)": 2.15, "Half Wave Wire Dipole": 2.15, "Vertical Multiband Telescopic": 0.0, "3-Element Yagi Beam": 7.0}
antenna_label = st.sidebar.selectbox("Antenna Configuration", list(antenna_options.keys()))
antenna_gain = antenna_options[antenna_label]

# Fetch Indices with fallbacks
@st.cache_data(ttl=3600)
def fetch_solar():
    return get_solar_indices()

@st.cache_data(ttl=3600)
def fetch_iono():
    return get_ionospheric_indices()

with st.sidebar:
    st.markdown("---")
    st.subheader("Live Solar & Ionospheric")
    with st.spinner("Fetching solar data..."):
        solar = fetch_solar()
        iono = fetch_iono()
    
    st.metric("Solar Flux Index (SFI)", solar.get('sfi', 100))
    st.metric("T-Index (ASWFC)", iono.get('t_index', 100), help="Australian Space Weather T-Index.")
    st.metric("SANSA State", iono.get('sansa_state', "Quiet"))
    st.metric("Planetary K-index", solar.get('kp', 2), delta=f"Penalty: {int(solar.get('kp', 2)*12)}%", delta_color="inverse")

# Main Logic
lat, lon = gs_to_latlon(gridsquare)

if not lat:
    st.error("Invalid Gridsquare.")
else:
    # 0. Layout Tabs
    tab_prop, tab_weather, tab_paths = st.tabs(["Propagation Forecast", "Weather & Elevation", "DX Paths & Map"])

    with tab_prop:
        # Calculations
        bands = [10, 20, 40]
        hours = list(range(24))
        rows = []
        for h in hours:
            row = {'UTC': h, 'Local (UTC+2)': (h + 2) % 24}
            for band in bands:
                row[f"{band}m"] = get_propagation_score(h, band, lat, lon, solar.get('sfi', 100), solar.get('kp', 2), power_w, antenna_gain, iono)
            rows.append(row)
        df = pd.DataFrame(rows)

        st.subheader("📊 Band Availability Forecast (24h)")
        c1, c2, c3 = st.columns(3)
        for i, band in enumerate(bands):
            b_name = f"{band}m"
            peak_row = df.loc[df[b_name].idxmax()]
            with [c1, c2, c3][i]:
                st.metric(f"{band}m Peak", f"{int(peak_row['UTC']):02d}:00 UTC", delta=f"Prob: {int(df[b_name].max()*100)}%")
                st.progress(df[b_name].max())

        chart_df = df.melt(id_vars=['UTC', 'Local (UTC+2)'], value_vars=['10m', '20m', '40m'], var_name='Band', value_name='Probability')
        fig = px.line(chart_df, x='UTC', y='Probability', color='Band', line_shape='spline', title="Hourly Propagation Probability", template="plotly_white")
        
        # Add vertical line for current UTC hour
        current_utc_hour = datetime.datetime.now(datetime.timezone.utc).hour
        fig.add_vline(x=current_utc_hour, line_width=3, line_dash="dash", line_color="red", annotation_text="NOW", annotation_position="top left")

        fig.update_xaxes(
            tickmode='linear',
            tick0=0,
            dtick=1,
            range=[-0.5, 23.5],
            title="Hour (UTC)"
        )
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Optimization Table")
        st.dataframe(df.style.background_gradient(cmap='Greens', subset=['10m', '20m', '40m']).format("{:.2f}", subset=['10m', '20m', '40m']), use_container_width=True)

    with tab_weather:
        weather_data = get_weather_and_elevation(lat, lon)
        activations = get_nearby_activations(lat, lon, gridsquare)
        
        w_col, sota_col = st.columns([1, 1])
        with w_col:
            if "error" not in weather_data:
                st.subheader(f"🌦️ Local Weather: {gridsquare}")
                wc1, wc2 = st.columns(2)
                wc1.info(f"**Elevation:** {int(weather_data.get('elevation', 0))}m")
                wc1.info(f"**Temp:** {weather_data.get('current_temp', 'N/A')}°C")
                wc2.info(f"**Humidity:** {weather_data.get('current_humidity', 'N/A')}%")
                wc2.info(f"**Wind:** {int(weather_data.get('current_wind', 0))} km/h")
                
                if 'hourly' in weather_data:
                    weather_df = pd.DataFrame({"Time": weather_data['hourly']['time'], "Temp (°C)": weather_data['hourly']['temperature_2m'], "Wind (km/h)": weather_data['hourly']['wind_speed_10m']})
                    st.plotly_chart(px.line(weather_df, x="Time", y="Temp (°C)", title="Temp Trend", template="plotly_white"), use_container_width=True)
            else:
                st.error(f"Weather data error: {weather_data['error']}")
        
        with sota_col:
            st.subheader("⛰️ Activation Locations")
            try:
                m_local = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker([lat, lon], popup="Home", icon=folium.Icon(color='red', icon='home')).add_to(m_local)
                
                # Plot SOTA Summits
                for sota in activations.get("sota", []):
                    s_lat = sota.get('latitude')
                    s_lon = sota.get('longitude')
                    if s_lat and s_lon:
                        folium.Marker(
                            [s_lat, s_lon], 
                            popup=f"SOTA: {sota.get('summitCode')} - {sota.get('summitName')}",
                            icon=folium.Icon(color='blue', icon='mountain', prefix='fa')
                        ).add_to(m_local)
                
                # Plot POTA Parks
                for pota in activations.get("pota", []):
                    p_lat = pota.get('latitude')
                    p_lon = pota.get('longitude')
                    if p_lat and p_lon:
                        folium.Marker(
                            [p_lat, p_lon], 
                            popup=f"POTA: {pota.get('reference')} - {pota.get('name')}",
                            icon=folium.Icon(color='green', icon='leaf', prefix='fa')
                        ).add_to(m_local)

                st_folium(m_local, width=500, height=350, key="local_map")
            except Exception:
                st.warning("Map display issue.")

            st_tab, po_tab = st.tabs(["SOTA", "POTA"])
            with st_tab:
                for sota in activations.get("sota", []):
                    st.markdown(f'<div class="activation-card"><a href="https://sotl.as/summits/{sota.get("summitCode")}" target="_blank" style="text-decoration:none; color:#1e293b;"><strong>{sota.get("summitCode")}</strong>: {sota.get("summitName")}<br><em>Elev: {sota.get("altitude")}m | Pts: {sota.get("points")}</em></a></div>', unsafe_allow_html=True)
            with po_tab:
                for pota in activations.get("pota", []):
                    st.markdown(f'<div class="activation-card" style="border-left-color: #22c55e;"><a href="https://pota.app/#/park/{pota.get("reference")}" target="_blank" style="text-decoration:none; color:#1e293b;"><strong>{pota.get("reference")}</strong>: {pota.get("name")}</a></div>', unsafe_allow_html=True)

    with tab_paths:
        st.subheader("🌍 Real-Time Global DX Heatmap (WSPR)")
        st.info("Showing actual signal paths from the last 60 minutes for stations near your gridsquare.")
        
        with st.spinner("Analyzing live WSPR spots..."):
            from utils import get_realtime_spots
            spots = get_realtime_spots(gridsquare)
        
        if spots:
            spot_df = pd.DataFrame(spots)
            
            selected_band = st.radio("Select Band for Heatmap", ["All Bands", "10m", "20m", "40m"], horizontal=True)
            if selected_band != "All Bands":
                display_df = spot_df[spot_df['band'] == selected_band]
            else:
                display_df = spot_df

            # Probability mapping based on SNR
            # SNR > 0: High (Green), -15 < SNR <= 0: Marginal (Orange), SNR <= -15: Low (Red)
            def map_prob(snr):
                if snr > 0: return 1.0 # High
                if snr > -15: return 0.6 # Marginal
                return 0.2 # Low
            
            display_df['Probability'] = display_df['snr'].apply(map_prob)
            
            if not display_df.empty:
                fig_heat = px.density_mapbox(
                    display_df, 
                    lat='lat', 
                    lon='lon', 
                    z='Probability', 
                    radius=15,
                    center=dict(lat=lat, lon=lon), 
                    zoom=1,
                    mapbox_style="carto-positron",
                    color_continuous_scale=[[0, 'red'], [0.5, 'orange'], [1.0, 'green']],
                    title=f"WSPR Propagation Heatmap ({selected_band})",
                )
                fig_heat.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.warning(f"No recent WSPR spots found for the {selected_band} band.")
        else:
            st.warning("No recent WSPR spots found near your location. Try a different gridsquare or check back later.")

        st.subheader("🌍 Theoretical World DX Path Map")
        try:
            targets = get_dx_targets()
            fig_map = go.Figure()
            fig_map.add_trace(go.Scattergeo(lon=[lon], lat=[lat], mode='markers', marker=dict(size=12, color='red'), name='Home'))
            
            dx_list = []
            for name, coords in targets.items():
                t_lat, t_lon = coords
                bearing = calculate_bearing(lat, lon, t_lat, t_lon)
                dist = calculate_distance(lat, lon, t_lat, t_lon)
                dx_list.append({"Region": name, "Bearing (°)": int(bearing), "Distance (km)": int(dist)})
                fig_map.add_trace(go.Scattergeo(lon=[lon, t_lon], lat=[lat, t_lat], mode='lines', line=dict(width=2, color='blue'), opacity=0.4, showlegend=False))
                fig_map.add_trace(go.Scattergeo(lon=[t_lon], lat=[t_lat], mode='markers', marker=dict(size=8, color='blue'), name=name))

            fig_map.update_layout(
                geo=dict(
                    showland=True, 
                    showcountries=True, 
                    projection_type="azimuthal equidistant",
                    projection_rotation=dict(lon=lon, lat=lat, roll=0),
                    showcoastlines=True,
                    landcolor="ivory",
                    oceancolor="LightBlue",
                    showocean=True,
                    lakecolor="LightBlue"
                ), 
                height=600, 
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig_map, use_container_width=True)
            
            st.subheader("📐 Path Analysis & Beam Bearings")
            st.table(pd.DataFrame(dx_list))
        except Exception as e:
            st.error(f"Path Map error: {e}")
