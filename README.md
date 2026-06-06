 # Dataviz — Glaciers Retreat

Data Visualization project  ...

 **Overview**

....

 **Requirements**

 - Python 3.9+ recommended.
 - A virtual environment is strongly recommended.
 - Project dependencies should be listed in `requirements.txt`. If this file is not present, install commonly used data/visualization packages such as `pandas`, `numpy`, `matplotlib`, `seaborn`, and `plotly`.

 **Setup**

 1. Create and activate a virtual environment:

 Windows (PowerShell):

 ```powershell
 python -m venv .venv
 .\\.venv\\Scripts\\Activate.ps1
 ```

 macOS / Linux:

 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```

 2. Install dependencies:

 ```bash
 pip install -r requirements.txt
 ```

 **Running the application**

 ```bash
 streamlit run Home.py
 ```

EDA for Italian situation: [notebooks/eda_unimi.ipynb](notebooks/eda_unimi.ipynb).
EDA for Global situations: [notebooks/bdv_wgms_eda.ipynb](notebooks/bdv_wgms_eda.ipynb)

 **Data**

 Place additional CSVs under `data/your-folder`. If the dataset is large, consider committing a sample subset and add instead instructions to retrieve the full data.

 **Contributing**

 - Clone the repository and create a topic branch: `git checkout -b feature/your-change`.
 - Keep changes focused and add tests/examples where applicable.
 - Run the project locally and ensure visual outputs render as expected.
 - Open a pull request describing the change and linking any related issues.

 Data contributions:

 - When adding new datasets, include a small sample (if the full dataset is large) and provide a data source citation in a `data/README.md` inside the relevant folder.
