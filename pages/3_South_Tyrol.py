import streamlit as st

from src.south_tyrol_plots import (
    make_map,
    make_aggregate_charts,
    make_regional_chart,
)

st.title("South Tyrol")
st.write("")


# ---------------------------------------------------------------------------
# 1. Interactive map
# ---------------------------------------------------------------------------
st.header("How much smaller did the glaciers become from 1997 to 2017?")
st.markdown("""
In the layers of this interactive map, you can see:

- **Relative change 1997→2017**: the percentage of area loss over 20 years for each glacier
- **Glacier extent in 1997, 2005, and 2017**: overlay them to see the change clearly

Hover over any glacier to see more information about it.
""")

st.markdown("**Show layers:**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    show_change = st.checkbox("Relative change 1997→2017", value=True)
with c2:
    show_1997 = st.checkbox("Glacier extent 1997", value=False)
with c3:
    show_2005 = st.checkbox("Glacier extent 2005", value=False)
with c4:
    show_2017 = st.checkbox("Glacier extent 2017", value=False)

fig_map = make_map(show_change, show_1997, show_2005, show_2017)
st.plotly_chart(
    fig_map,
    use_container_width=True,
    config={"scrollZoom": True},
)
st.write("")


# ---------------------------------------------------------------------------
# 2. Aggregate stats
# ---------------------------------------------------------------------------
st.header("The glaciers are fragmenting")
st.markdown(
    "As glaciers melt, they split into more pieces. "
    "The bar charts below show this clearly: the total ice area shrinks, "
    "the number of parts grows, and the average part becomes smaller."
)

fig_area, fig_count, fig_size = make_aggregate_charts()
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(fig_area, use_container_width=True)
with col2:
    st.plotly_chart(fig_count, use_container_width=True)
with col3:
    st.plotly_chart(fig_size, use_container_width=True)

st.write("")


# ---------------------------------------------------------------------------
# 3. Regional change
# ---------------------------------------------------------------------------
st.header("Which mountain groups lost the most ice?")
st.markdown(
    "The chart below shows how each mountain group's ice changed "
    "between 1997 and 2017. Every region lost area — but the losses are "
    "far from uniform. Smaller, fragmented glaciers in the eastern groups "
    "retreated fastest."
)

st.plotly_chart(make_regional_chart(), use_container_width=True)
st.write("")