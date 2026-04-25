# Conda Environment Setup

**Live Application:** [https://dx-predictor.streamlit.app/](https://dx-predictor.streamlit.app/)

To run DXPredictor, please use the `dx_env` conda environment.

## Activating the Environment
```bash
conda activate dx_env
```

## Environment Details
- **Path:** `/home/mark/miniconda3/envs/dx_env`
- **Python Version:** Python 3.13.12 (as per `conda info`)
- **Main Dependencies:**
  - `streamlit`
  - `maidenhead`
  - `pandas`
  - `plotly`
  - `folium`
  - `streamlit-folium`

## Running the Application
```bash
export PYTHONPATH=$PYTHONPATH:.
/home/mark/miniconda3/envs/dx_env/bin/streamlit run src/app.py
```

## Running Tests
```bash
export PYTHONPATH=$PYTHONPATH:.
/home/mark/miniconda3/envs/dx_env/bin/python3 test_gs_logic.py
```
