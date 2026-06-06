# Glaciers Retreat

This project provides an interactive data visualization dashboard showing glacier change (area, mass balance, and regional summaries) using Streamlit and Plotly. It collects processed WGMS datasets, regional shapefiles, historical mappings and example analyses for Italy and South Tyrol.

## Requirements

- Python 3.9+ (3.12 tested in development).
- A virtual environment is strongly recommended.

## Quick run (local)

1. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

**Run (Streamlit)**

Start the app from the repository root:

```bash
streamlit run Home.py
```

Open http://localhost:8501 in your browser.

## Run with Docker

Build the image (from repo root, where `docker/Dockerfile` lives):

```bash
docker build -t streamlit-glaciers -f docker/Dockerfile .
docker run -p 8501:8501 streamlit-glaciers
```
