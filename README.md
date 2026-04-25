# 📡 DXPredictor

SOTA/POTA HF DX Propagation & Path Forecast by ZS6MDX.

## 🚀 Live Application
The application is live and can be accessed at:
**[https://dx-predictor.streamlit.app/](https://dx-predictor.streamlit.app/)**

## Overview
DXPredictor is a Streamlit-based tool designed for amateur radio enthusiasts (SOTA/POTA). It provides:
- **Real-Time Solar & Ionospheric Data**: Fetches live SFI, SSN, Kp, and T-Index.
- **Hourly Propagation Forecast**: Predicts band availability (10m, 20m, 40m) based on current conditions.
- **Global WSPR Heatmap**: Visualizes real-time communication paths using the WSPR.live network.
- **Weather & Activations**: Local weather forecasts and nearby SOTA/POTA activation spots.

## Local Setup
For local development and testing, please refer to:
- [CONDA_SETUP.md](CONDA_SETUP.md): Environment setup and running instructions.
- [DEPLOYMENT.md](DEPLOYMENT.md): Guide for deploying to Streamlit Community Cloud.

## Data Sources
- **Solar/Space Weather**: NOAA (SWPC), ASWFC (Australia), SANSA (South Africa).
- **Propagation Spots**: WSPR.live (ClickHouse DB).
- **Weather**: MET Norway.
- **Activations**: POTA.app and SOTA.org.uk APIs.
