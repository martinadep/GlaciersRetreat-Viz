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

############## ITALY only ###############
if selected_region is None:
    col1, col2 = st.columns(2)

    # ----------- maps -----------
    with col1:
        italy_count_map = it.region_counts_map(df)
        st.plotly_chart(italy_count_map, use_container_width=True)

    with col2: 
        italy_area_map = it.region_area_map(df)
        st.plotly_chart(italy_area_map, use_container_width=True)

    st.markdown("*Data Source: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan.*")

    st.markdown(
        """
        <div style="font-size: 18px; line-height: 1.6; margin-top: 15px; margin-bottom: 15px;">
            Although <b>Trentino - Alto Adige</b> (329) and <b>Lombardy</b> (230) are the Italian regions with the highest glacier counts, 
            <b>Aosta Valley</b> dominates in terms of total glacier area, hosting the largest coverage. 
            This highlights that glacier distribution in Italy is <b>non-uniform</b>, with a <b>few vast, resilient glaciers</b> 
            and <b>many highly fragmented formations</b>.
        </div>
        """, 
        unsafe_allow_html=True
    )
####################################

 # ----------- barplots area / count -----------
tab_area, tab_count = st.tabs(["Glacier Area Shrinkage", "Glacier Count Evolution"])
with tab_area:
    area_comparison_fig = it.historical_area(df, region=selected_region)
    st.plotly_chart(area_comparison_fig, use_container_width=True)
    if selected_region is None: 
        st.markdown("*Data Sources: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan*")    
    else:
        st.markdown("*Data Sources: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan*")

with tab_count:
    count_comparison_fig = it.historical_counts(df, df_porro=df_porro, region=selected_region)
    st.plotly_chart(count_comparison_fig, use_container_width=True) 
    st.markdown("""
                *Data Sources: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan, \
                    and **Il Nuovo Catasto dei Ghiacciai Italiani (1926)**, Carlo Porro*
                """)
    
st.markdown("""
    <div style="font-size: 18px; line-height: 1.6; margin-top: 15px; margin-bottom: 15px;">
        Under global climate warming, <b>glaciers in the Italian Alps are retreating and fragmenting</b>, with a significant reduction in area and increase in count. 
        However, the broad difference in technique, methods and data sources between the new Inventory and the old ones should also be considered. 
        Such profound differences cast doubt on the results obtained; in several cases the changes in Italian glaciation over the last half-century may 
        have been underestimated. 
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------- new formations and aspect distribution ----------
col1, col2 = st.columns(2)
with col1:
    fragmented_barchart_fig = it.fragmented_barchart(df, region=selected_region)
    st.plotly_chart(fragmented_barchart_fig, use_container_width=True)
with col2:
    compass_plot_fig = it.compass_aspect(df)
    st.plotly_chart(compass_plot_fig, use_container_width=True)
st.markdown("*Data Source: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan.*")
st.markdown("---")
# ------------ glacier types distribution -----------
col1, col2, col3 = st.columns(3)
with col1:
    pie_types_fig = it.pie_glacier_types(df, region=selected_region)
    st.plotly_chart(pie_types_fig, use_container_width=True)
with col2:
    pie_types_area_fig = it.pie_glacier_types_area(df, region=selected_region)
    st.plotly_chart(pie_types_area_fig, use_container_width=True)
with col3:
    st.markdown(
        """
        <div style="font-size: 18px; line-height: 1.6; margin-top: 15px; margin-bottom: 15px;">
            <b>GLACIER TYPES</b>
            <ul>
                <li><strong>Mountain glacier</strong>: a glacier, even of considerable size, which does not develop an ablation tongue and which is located on mountain slopes.</li>
                <li><strong>Glacieret</strong>: restricted ice body of unclear shape and morphology, with slow or absent ice flow. This type is attributed to all the ice bodies featuring a surface area less than 0.5 km2.</li>
                <li><strong>Valley glacier</strong>: an ice body featuring an accumulation basin from which originates an ablation tongue flowing downward between the walls of the valley, which needs to be clearly shaped and evident from a geomorphological point of view.</li>
            </ul>
            <br>
            <em>Ablation tongue</em>: the elongated section of a glacier that extends into warmer elevations.
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("*Data Source: **New Glacier Inventory (2016)**, developed and published by the Earth Science Department of the University of Milan.*")
st.markdown("---")

# ------ Interactive Table ------
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