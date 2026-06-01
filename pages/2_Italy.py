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

col1, col2 = st.columns(2)
with col1:
    if selected_region == "ALL":
        st.markdown("#### Showing data for: **All Regions (Italy)**")
        # Se seleziona "All", passiamo region=None alla tua funzione
        bar_sector_counts_fig = it.bar_sector_counts(df, region=None)
    else:
        st.markdown(f"#### Showing data for region: **{selected_region}**")
        bar_sector_counts_fig = it.bar_sector_counts(df, region=selected_region)
    st.subheader("Glacier Counts")
    st.plotly_chart(bar_sector_counts_fig, use_container_width=True)

with col2:
    if selected_region == "ALL":
        st.markdown("#### Showing data for: **All Regions (Italy)**")
        # Se seleziona "All", passiamo region=None alla tua funzione
        bar_sector_counts_fig2 = it.bar_sector_counts(df, region=None)
    else:
        st.markdown(f"#### Showing data for region: **{selected_region}**")
        bar_sector_counts_fig2 = it.bar_sector_counts(df, region=selected_region)
        st.subheader("Glacier Distribution")
        st.plotly_chart(bar_sector_counts_fig2, use_container_width=True)


# ------ Interactive Table ------
st.markdown(""" 
            #### New Glacier Inventory (2016)""")

interactive_table(df, caption='Italian Glaciers',
                  select=True,
                  classes=['nowrap', 'compact', 'display', 'stripe'],
                  buttons=['csvHtml5', 'colvis', 'pageLength'])

