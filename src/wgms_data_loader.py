import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data  # Ottimizza le prestazioni mantenendo i dati in memoria

def load_wgms_global():
    df_global = pd.read_csv('./data/wgms-amce-2026-02-10/global.csv')
    return df_global

def load_wgms_global_mmsle():
    df_global=pd.read_csv('./data/wgms-amce-2026-02-10/global.csv')
    df_global_mmsle = df_global[['year', 'mmsle']].copy()
    # already tidy, no need to melt

    return df_global_mmsle

def load_wgms_regions_areakm2(code='total', year_range=None):
    if code == 'total':
        df_area = pd.DataFrame()
        for el in ['ACN','ACS','ALA','ANT','ASC','ASE','ASN','ASW','CAU','CEU','GRL','ISL','NZL','RUA','SA1','SA2','SCA','SJM','TRP','WNA']:
            
            df = pd.read_csv(f'./data/wgms-amce-2026-02-10/region/{el}.csv')
            df_area[el] = df.set_index('year')['area_km2']
    
    else:
        df = pd.read_csv(f'./data/wgms-amce-2026-02-10/region/{code}.csv')
        df_area= df.set_index('year')[['area_km2']]
    
    if year_range is not None:
        start, end = year_range
        df_area = df_area.loc[start:end]
    
    df_tidy = df_area.reset_index().melt(
    id_vars='year',
    var_name='region',
    value_name='area_km2')
    
    return df_tidy

# print(load_wgms_regions_areakm2().head())


def load_wgms_regions_gt(code='total', year_range=None):
    # returns a dataframe containing the mass change in gigatonnes (Gt) for the specified region and year range.
    
    if code == 'total':
        df_gt = pd.DataFrame()
        for el in ['ACN','ACS','ALA','ANT','ASC','ASE','ASN','ASW','CAU','CEU','GRL','ISL','NZL','RUA','SA1','SA2','SCA','SJM','TRP','WNA']:
            
            df = pd.read_csv(f'./data/wgms-amce-2026-02-10/region/{el}.csv')
            df_gt[el] = df.set_index('year')['gt']
    
    else:
        df = pd.read_csv(f'./data/wgms-amce-2026-02-10/region/{code}.csv')
        df_gt = df.set_index('year')[['gt']]
    
    if year_range is not None:
        start, end = year_range
        df_gt = df_gt.loc[start:end]
    
    df_tidy = df_gt.reset_index().melt(
    id_vars='year',
    var_name='region',
    value_name='gt')
    
    return df_tidy



