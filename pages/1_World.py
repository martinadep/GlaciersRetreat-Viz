import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


from src.data_loader import *
from src.wgms_data_loader import *

st.title("🌍 What is happening around the world?")
# st.markdown(body="Glaciers are retreating globally, with significant mass loss observed in many regions. The overall trend is a decrease in glacier mass and area, contributing to rising sea levels and impacting ecosystems and water resources worldwide.")

st.markdown("""
Glaciers are Earth's frozen memory, accumulating snow over centuries and releasing it slowly, 
regulating river flow, sea levels, and regional climates. Since the mid-20th century, this memory 
is being erased at an accelerating pace. Across nearly every region on the planet, glaciers are 
shrinking: losing mass, retreating upslope, and in some cases disappearing entirely. 
The World Glacier Monitoring Service estimates that glaciers worldwide lost an average of almost **295 Gt of ice per year** 
between 2000 and 2025, enough to cover the entire surface of Switzerland under 6 meters of water, every year.
""")

st.header("What glaciers are we talking about?")

st.markdown("""
This website draws on data from the **World Glacier Monitoring Service (WGMS)**, following the 
**Randolph Glacier Inventory (RGI)** catalogation, which is the most comprehensive global collection of glaciers, 
covering over 215,000 individual glaciers across 19 regions, working as a census of the world's ice.

The map below shows where these glaciers are distributed. Roughly half of the world's glacier area is concentrated in just a few regions: 
Antarctica & Subantarctic, Arctic Canada, and Greenland's periphery.""")

from visualizations.glacier_region_map import interactive_global_grid_glacier_regions

fig = interactive_global_grid_glacier_regions()
st.plotly_chart(fig, use_container_width=True)
st.caption("""Data from 
WGMS (2026). Annual mass-change estimates for the world's glaciers. Individual glacier time series and gridded data products. https://doi.org/10.5904/wgms-amce-2026-02-10""")



# st.header("Glacier area Change (km²)")
# st.markdown(body="This map shows the percentage change in glacier area over time, " \
# "from the first observed measurement in the wgms dataset (1965). The darked the shade of red, the higher the change. " \
# "Over these 60 years, the most dramatic changes seem to be in the regions of Central America," \
# " the Andes, Central Europe, Africa and south-Eastern Asia, where the surface loss has decreased by over 40 percentage points in 2025 " \
# "")

st.header("Relative Glacier Surface Area Change")
st.markdown("""
This map animates the **percentage loss in glacier surface area** relative to each glacier's 
earliest recorded measurement in the WGMS dataset. Surface area is a leading indicator of glacier health: 
as a glacier shrinks horizontally, it exposes darker rock and soil, which absorbs more 
solar radiation and accelerates further melting: this phenomenon is known as the **ice-albedo effect**.""")
from visualizations.interactive_global_areakm2_pctloss import interactive_global_grid_pctloss

# inspect rate of decrease
# fig = interactive_global_areakm2()
fig=interactive_global_grid_pctloss()
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.caption("""Data from 
WGMS (2026). Annual mass-change estimates for the world's glaciers. Individual glacier time series and gridded data products. https://doi.org/10.5904/wgms-amce-2026-02-10""")
st.markdown("""The most dramatic losses, exceeding **40% of original surface area**, are concentrated in 
tropical and mid-latitude regions: the **tropical Andes**, **Central Europe** (Alps), 
**East Africa**, and **Southeast Asia**. These are also regions where glaciers sit at lower 
altitudes with no cold arctic buffer. In contrast, polar regions like **Greenland** and **Arctic Canada**
 show smaller percentage losses, as they have more extensive ice cover and colder climates.
""")

st.header('Global millimeter sea level equivalent')
# st.markdown(body="Mass change in millimeters of sea level equivalent (mm SLE) over time, from the first observed measurement (1965)")
from visualizations.interactive_global_mmsle import interactive_global_mmsle

# st.header("Global Millimeter Sea Level Equivalent (mm SLE)")
st.markdown("""
When glaciers melt, their water flows into the ocean, raising sea levels globally. 
The **millimeter sea level equivalent (mm SLE)** converts glacier mass loss into its 
direct impact on global mean sea level.
Each bar in this chart represents how much global sea level *would rise* from that year's 
glacier mass loss alone, if spread evenly across all the world's oceans. 
""")


fig = interactive_global_mmsle()
st.plotly_chart(fig, use_container_width=True)
st.caption("""Data from 
WGMS (2026). Annual mass-change estimates for the world's glaciers. Individual glacier time series and gridded data products. https://doi.org/10.5904/wgms-amce-2026-02-10""")

st.markdown("""The WGMS reports that glaciers (excluding the Greenland and Antarctic ice sheets) have 
contributed approximately **26 mm of sea level rise since 1976**. 
For coastal cities like Miami, Jakarta, or Venice, every millimeter matters.""")

st.header('Regional mass change in giga tonnes')
# st.markdown(body="Mass change in gigatonnes (Gt) for different regions over time, from the first observed measurement (1965), select the region and lok at how glacier mass has changed. The overall global trend, after the 1990s, is negative.")

st.markdown("""
This chart shows how glacier **mass**, measured in gigatonnes (Gt), has evolved across 
different regions over time.
            
Mass change is arguably the most direct measure of a glacier's health. Unlike area, 
which shrinks only at the edges, mass captures losses happening throughout the glacier's 
entire volume.

The global signal is stark: after the **1990s**, virtually every region shows an accelerating 
negative trend. This acceleration coincides with a period of rapid atmospheric warming, 
and research (Zemp et al., 2019, *Nature*) confirms that the rate of glacier mass loss 
has **doubled since the 1990s** compared to the preceding decades. 
Use the dropdown to explore individual regions and see how local trends compare to the global picture.
""")

from visualizations.interactive_region_gt import *
fig =  create_region_gt()
st.plotly_chart(fig, use_container_width=True)
st.caption("""Data from 
WGMS (2026). Annual mass-change estimates for the world's glaciers. Individual glacier time series and gridded data products. https://doi.org/10.5904/wgms-amce-2026-02-10""")

st.divider()
st.caption("""
**References**  
Zemp, M., et al. (2019). Global glacier mass changes and their contributions to sea-level rise from 1961 to 2016. *Nature*, 568, 382–386. https://doi.org/10.1038/s41586-019-1071-0
Dussaillant, I., Hugonnet, R., Huss, M., Berthier, E., Bannwart, J., Paul, F., and Zemp, M. (2025). Annual mass change of the world's glaciers from 1976 to 2024 by temporal downscaling of satellite data with in-situ observations. *Earth System Science Data*, 17(5), 1977–2006. https://doi.org/10.5194/essd-17-1977-2025
""")