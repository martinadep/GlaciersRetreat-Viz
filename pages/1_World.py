import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


from src.data_loader import *
from src.wgms_data_loader import *
from visualizations import interactive_global_areakm2




# st.title("🗺️ Interactive Glacier Retreat Map")

# # 1. Load data from the centralized module
# df = load_glacier_data()

# # 2. Create filters on the sidebar or page
# st.subheader("Filter data by year")
# min_anno = int(df['anno'].min())
# max_anno = int(df['anno'].max())

# # The slider captures the year selected by the user
# anno_selezionato = st.slider("Select the Year", min_anno, max_anno, max_anno)

# # 3. Filter the dataset based on the slider value
# df_filtrato = df[df['anno'] == anno_selezionato]

# # 4. Create the interactive map with Plotly Express
# fig = px.scatter_mapbox(
#     df_filtrato,
#     lat="latitude",
#     lon="longitude",
#     size="ritiro_metri",
#     color="temperatura_anomalia",
#     hover_name="nome",
#     size_max=30,
#     zoom=5,
#     mapbox_style="open-street-map", # Free map style that does not require an API token
#     title=f"Glacier Status in the Year {anno_selezionato}",
#     color_continuous_scale=px.colors.sequential.Reds
# )

# fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

# # 5. Display the map on the web page
# st.plotly_chart(fig, use_container_width=True)

# # Also display a table with the filtered data below the map (optional)
# st.write("Detailed data for the selected year:", df_filtrato)

st.title("🗺️ Glacier area Change (km²)")
from visualizations.interactive_global_areakm2_pctloss import interactive_global_grid_pctloss

# fig = interactive_global_areakm2()
fig=interactive_global_grid_pctloss()
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.title('Global mmsle')

from visualizations.interactive_global_mmsle import interactive_global_mmsle

fig = interactive_global_mmsle()
st.plotly_chart(fig, use_container_width=True)

st.title('Regional mass change (Gt)')
from visualizations.interactive_region_gt import *
fig =  create_region_gt()
st.plotly_chart(fig, use_container_width=True)