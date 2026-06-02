import streamlit as st
import pandas as pd
import src.italy_plots as it
from itables.streamlit import interactive_table

# st.title("🗺️ Interactive Glacier Retreat Map")

# ----------------------- Load Data and choose region -----------------------
df = it.load_data()

region_options = ["ALL - Italy"] + list(df["Region"].unique())
selected_region = st.selectbox("Select a Region", options=region_options)

if selected_region == "ALL - Italy":
    selected_region = None

else:
    df = df[df["Region"] == selected_region]

# ------ Glacier Count by Mountain Sector -------- Aspect Compass ----------
col1, col2 = st.columns(2)
with col1:
    bar_sector_counts_fig = it.bar_sector_counts(df, region=selected_region)
    st.plotly_chart(bar_sector_counts_fig, use_container_width=True)

with col2:
    compass_plot_fig = it.compass_aspect(df)
    st.plotly_chart(compass_plot_fig, use_container_width=True)

# ------ sunburst and tree ------
# col1, col2 = st.columns(2)
# with col1:
#     sunburst_fig = it.sunburst_counts(df)
#     st.plotly_chart(sunburst_fig, use_container_width=True)

# with col2:
#     tree_fig = it.tree(df)
#     st.plotly_chart(tree_fig, use_container_width=True)

# ----------- Italy Map -----------
if selected_region is None:
    # tab1, tab2 = st.tabs(["Glacier count", "Glacier Area Timeline ⏳"])
    col1, col2 = st.columns(2)

    with col1:
        italy_map = it.map_glaciers_by_region(df)
        st.plotly_chart(italy_map, use_container_width=True)
        
        line_count_fig = it.line_count_trend(df)
        st.plotly_chart(line_count_fig, use_container_width=True)


    with col2:
        italy_area_map = it.map_glaciers_area_by_region(df)# area_col=chosen_area_column)
        st.plotly_chart(italy_area_map, use_container_width=True)
                
        line_area_fig = it.line_area_trend(df)
        st.plotly_chart(line_area_fig, use_container_width=True)



# ------ Interactive Table ------
st.markdown(""" 
            #### New Glacier Inventory (2016)""")

# Wrap interactive table in a full-width container so CSS can stretch it to page width
st.markdown('<div class="full-width-table">', unsafe_allow_html=True)
interactive_table(df, caption='Italian Glaciers',
                  select=True, maxBytes=0,
                  classes=['nowrap', 'compact', 'display', 'stripe'],
                  buttons=['csvHtml5', 'colvis', 'pageLength'])
st.markdown('</div>', unsafe_allow_html=True)

