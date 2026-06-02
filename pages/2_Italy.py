import streamlit as st
import pandas as pd
import src.italy_plots as it
from itables.streamlit import interactive_table

# ----------------------- Load Data and choose region -----------------------
df = it.load_data()
df_porro = it.load_porro_data()

region_options = ["ALL - Italy"] + list(df["Region"].unique())
selected_region = st.selectbox("Select a Region", options=region_options)

if selected_region == "ALL - Italy":
    selected_region = None
else:
    df = df[df["Region"] == selected_region]


if selected_region is None:
    col1, col2 = st.columns(2)
    # ----------- italian maps -----------
    with col1:
        italy_count_map = it.region_counts_map(df)
        st.plotly_chart(italy_count_map, use_container_width=True)

    with col2: 
        italy_area_map = it.region_area_map(df)
        st.plotly_chart(italy_area_map, use_container_width=True)
    
    st.info("**Geographical Insight:** A significant geographic contrast is evident across the Italian cryosphere. While regions such as Lombardy (230 glaciers) and South Tyrol (213 glaciers) register the highest number of individual bodies, Aosta Valley sharply dominates the country in terms of cumulative spatial area. This demonstrates that glacier distribution is highly non-uniform: a few vast, resilient glaciers dominate the landscape over smaller, highly fragmented formations.")
st.markdown("---")
   
# ----------- region area comparison bar chart -----------
tab_area, tab_count = st.tabs(["Glacier Area Shrinkage", "Glacier Count Evolution"])

with tab_area:
    area_comparison_fig = it.historical_area(df, region=selected_region)
    st.plotly_chart(area_comparison_fig, use_container_width=True)
    if selected_region is None:
        st.info("**Data Quality & Trend Analysis:** While a critical reduction in glacier surface area is visible since the CGI inventory (1959-1962), the intermediate WGI data (late 1970s) can exhibit artificial inflation[cite: 1]. As documented, the original WGI aerial photos suffered from significant snow coverage, which occasionally led to overestimating historical areas and underestimating the actual half-century retreat[cite: 1]. Note that recent measurements represent a *2005-2013 range* due to regional survey discrepancies[cite: 1].")
    else:
        st.info(f"**Regional Focus ({selected_region}):** The detailed breakdown by Mountain Group demonstrates that area shrinkage is highly localized[cite: 1]. High-altitude massifs partially resist thanks to lower temperatures at their accumulation zones, whereas lower mountain groups are undergoing near-total deglaciazione[cite: 1].")

with tab_count:
    count_comparison_fig = it.historical_counts(df, df_porro=df_porro, region=selected_region)
    st.plotly_chart(count_comparison_fig, use_container_width=True) 
    st.info("**Fragmentation & Typology:** The 'Newly Formed' status (derived from split ID codes) identifies fragments lacking previous separate inclusion in historical inventories. Although smaller classifications like glacierets often represent a massive percentage of the total glacier count, they account for a minimal fraction of the total area, which remains dominated by mountain glaciers.")
   
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    # ----------- bar chart of sector counts -----------
    newly_formed_barchart_fig = it.newly_formed_barchart(df, region=selected_region)
    st.plotly_chart(newly_formed_barchart_fig, use_container_width=True)
    st.markdown("<small>**Fragmentation & Typology:** The 'Newly Formed' status (derived from split ID codes) identifies fragments lacking previous separate inclusion in historical inventories. Although smaller classifications like glacierets often represent a massive percentage of the total glacier count, they account for a minimal fraction of the total area, which remains dominated by mountain glaciers.</small>", unsafe_allow_html=True)
with col2:
    # ----------- compass plot of aspect distribution -----------
    compass_plot_fig = it.compass_aspect(df)
    st.plotly_chart(compass_plot_fig, use_container_width=True)
    st.markdown("<small>**Geomorphological Orientation:** Glacial conservation heavily favors northern aspects. West and East alignments are less populated because the Alps primarily extend along lines of latitude. Interestingly, North-West features a higher count of smaller glaciers, whereas North-East hosts fewer but significantly wider ones.</small>", unsafe_allow_html=True)

# # comments
# col_txt1, col_txt2 = st.columns(2)
# with col_txt1:
#     st.markdown("<small>**Fragmentation Analysis:** The light red bars represent 'Newly Formed' glaciers. A high count of newly detached units (e.g., in the Rhaetian Alps) is not an indicator of glacial growth, but rather a direct symptom of large glaciers breaking apart into smaller, more vulnerable remnants.</small>", unsafe_allow_html=True)
# with col_txt2:
#     st.markdown("<small>**Geomorphological Orientation:** The polar compass chart reveals a strong environmental asymmetry. Both glacier count and total surface area heavily cluster around the northern quadrants (N, NW, NE). South-facing slopes suffer from direct solar radiation that accelerates melting, leaving very few stable glacial bodies.</small>", unsafe_allow_html=True)

# ------ Interactive Table ------
st.markdown("---")
st.markdown("""#### New Glacier Inventory (2016)""")
df_display = df.copy()
df_display['Area CGI (km2)'] = df_display['Area CGI (km2)'].map(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
df_display['Area WGI (km2)'] = df_display['Area WGI (km2)'].map(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
df_display['Area (km2)'] = df_display['Area (km2)'].map(lambda x: f"{x:.2f}" if pd.notna(x) else "-")

st.markdown('<div class="full-width-table">', unsafe_allow_html=True)
interactive_table(df_display, caption='Italian Glaciers',
                  select=True, maxBytes=0,
                  classes=['nowrap', 'compact', 'display', 'stripe'],
                  buttons=['csvHtml5', 'colvis', 'pageLength'])
st.markdown('</div>', unsafe_allow_html=True)