# Deployment Guide: DXPredictor

This document explains how to deploy the **DXPredictor** application for free.

## Project Analysis
The DXPredictor is a **Streamlit** application designed for amateur radio enthusiasts (SOTA/POTA).
- **Core Technology:** Python 3.x
- **Main Framework:** Streamlit (for the web interface)
- **Data Sources:** Uses public APIs (NOAA, ASWFC, SANSA) that do not require paid subscriptions or API keys.
- **Dependencies:** Standard data science and mapping libraries (`pandas`, `plotly`, `folium`, `requests`).

## Recommended Hosting: Streamlit Community Cloud
For a beginner, the best way to host this app for **$0/month** is **Streamlit Community Cloud**.

### Why this option?
1. **Completely Free:** No credit card required for public repositories.
2. **Easy for Beginners:** Once set up, it updates your website automatically whenever you change your code.
3. **Optimized Performance:** It is built specifically to run Streamlit apps smoothly.

---

## Step-by-Step Deployment Process

### 1. Upload your code to GitHub
Streamlit Community Cloud works by "reading" your code from a GitHub repository.
1. Create a free account at [GitHub.com](https://github.com).
2. Create a new repository named `DXPredictor`.
3. Upload all the files from your project folder to this repository.
   - **Crucial files to include:** `src/`, `requirements.txt`, and `.streamlit/config.toml`.

### 2. Connect to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **"Continue with GitHub"** and sign in.
3. Once logged in, click the **"Create app"** button.

### 3. Deploy the App
In the "Deploy an app" window, fill in the following:
- **Repository:** Select your `yourusername/DXPredictor` repo.
- **Branch:** Usually `main` or `master`.
- **Main file path:** `src/app.py` (This is the entry point of your app).
- **App URL:** You can customize this (e.g., `dx-predictor.streamlit.app`).

Click **"Deploy!"** and wait about 2-3 minutes. Your app will be live on the internet!

---

## Important Maintenance Tips
- **The "Sleep" Mode:** If no one visits your site for a few days, Streamlit will put it to "sleep" to save energy. Don't worry—the first person to visit it after that will see a "Wake up" button.
- **requirements.txt:** This file tells the server which libraries to install. If you add new features using new libraries, remember to add them to this file.
- **Privacy:** Since this is a public repository, never put passwords or private API keys directly in your code. (Though this specific project doesn't currently use any).

## Alternative Options (Optional)
If you ever outgrow Streamlit Cloud, you can look into:
- **Hugging Face Spaces:** Also free, very popular for data apps.
- **Render.com:** Offers a free tier but the app "spins down" and takes 30 seconds to start up when someone visits.
