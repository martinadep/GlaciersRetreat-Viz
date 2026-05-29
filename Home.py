import streamlit as st

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Glacier Retreat Dashboard",
    page_icon="🏔️",
    layout="wide"
)

# 2. Define all pages pointing to your target files
home_page = st.Page("Home.py", title="Home") 
world_page = st.Page("pages/1_World.py", title="World")
italy_page = st.Page("pages/2_Italy.py", title="Italy")
aa_page = st.Page("pages/3_South_Tyrol.py", title="South Tyrol")

# 3. Initialize navigation and completely hide the sidebar
pg = st.navigation([home_page, world_page, italy_page, aa_page], position="hidden")

# 4. Navigation Bar Layout
# Layout allocation: Left side for Home, center space for the 3 main buttons
col_home, _, col1, col2, col3, _ = st.columns([0.5, 1.5, 1, 1, 1, 2])

# Home button sits comfortably on the far left
with col_home:
    if st.button("🏠", use_container_width=True, type="primary" if pg == home_page else "secondary"):
        st.switch_page(home_page)

# The 3 navigation buttons stay clustered in the middle
with col1:
    if st.button("World", use_container_width=True, type="primary" if pg == world_page else "secondary"):
        st.switch_page(world_page)

with col2:
    if st.button("Italy", use_container_width=True, type="primary" if pg == italy_page else "secondary"):
        st.switch_page(italy_page)

with col3:
    if st.button("South Tyrol", use_container_width=True, type="primary" if pg == aa_page else "secondary"):
        st.switch_page(aa_page)

st.divider()

# 5. Page Router Execution
if pg == home_page:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>home</h1>", unsafe_allow_html=True)
else:
    pg.run()