import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data  # Ottimizza le prestazioni mantenendo i dati in memoria
def load_glacier_data():
    # Quando avrai i dati veri, userai: pd.read_csv("data/processed/tuo_file.csv")
    
    # Generiamo dati di prova (Mock Data) per il test iniziale
    anni = np.arange(2000, 2025)
    data_mappa = []
    
    # Creiamo coordinate finte per alcuni ghiacciai (es. Alpi)
    ghiacciai = [
        {"nome": "Ghiacciaio del Monte Bianco", "lat": 45.83, "lon": 6.86},
        {"nome": "Ghiacciaio della Marmolada", "lat": 46.43, "lon": 11.85},
        {"nome": "Ghiacciaio del Gorner", "lat": 45.96, "lon": 7.77}
    ]
    
    for g in ghiacciai:
        for anno in anni:
            data_mappa.append({
                "anno": anno,
                "nome": g["nome"],
                "latitude": g["lat"],
                "longitude": g["lon"],
                # Il ritiro aumenta con gli anni
                "ritiro_metri": (anno - 1999) * np.random.uniform(1.2, 2.5),
                "temperatura_anomalia": np.random.uniform(0.5, 2.1)
            })
            
    df_mappa = pd.DataFrame(data_mappa)
    return df_mappa