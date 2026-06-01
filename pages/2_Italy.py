import streamlit as st
import pandas as pd
import src.italy_plots as it
from itables.streamlit import interactive_table

st.title("🗺️ Interactive Glacier Retreat Map")

# ------ Load Data ------
df = it.load_data()


# ------ Interactive Plot: Glacier Count by Mountain Sector ------
region_options = ["ALL"] + list(df["Region"].unique())
selected_region = st.selectbox("Select a Region", options=region_options)

if selected_region == "ALL":
    selected_region = None
    st.markdown("#### Showing data for **all regions**")
else:
    st.markdown(f"#### Showing data for region: **{selected_region}**")

col1, col2 = st.columns(2)
with col1:
    bar_sector_counts_fig = it.bar_sector_counts(df, region=selected_region)
    st.plotly_chart(bar_sector_counts_fig, use_container_width=True)

with col2:
    compass_plot_fig = it.compass_aspect(df, region=selected_region)
    st.plotly_chart(compass_plot_fig, use_container_width=True)


# ------ Interactive Table ------
st.markdown(""" 
            #### New Glacier Inventory (2016)""")

interactive_table(df, caption='Italian Glaciers',
                  select=True,
                  classes=['nowrap', 'compact', 'display', 'stripe'],
                  buttons=['csvHtml5', 'colvis', 'pageLength'])

