import streamlit as st
from streamlit_image_comparison import image_comparison
import src.utils as utils
import plotly.graph_objects as go
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Glacier Retreat Dashboard",
    page_icon="🏔️",
    layout="wide"
)

utils.load_local_css("style.css")

# --- CUSTOM TRACKING & ROUTING MECHANISM ---
# Initialize session state for tracking current page location
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# 2. Render Top-Left Home Button conditionally
# Only display the home button if we aren't already on the Home page
if st.session_state.current_page != "Home":
    col_home, _ = st.columns([0.1, 0.9])
    with col_home:
        if st.button("🏠", use_container_width=False, type="secondary"):
            st.session_state.current_page = "Home"
            st.rerun()


# 3. PAGE ROUTER EXECUTION
if st.session_state.current_page == "Home":
    
    # Center-align custom text styles
    st.markdown(
        """
        <style>
        .centered-text {
            text-align: center;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Header 
    st.markdown(
        "<h1 class='centered-text'>Visualizing climate change<br>through glacier retreat</h1>", 
        unsafe_allow_html=True
    )

    # Subheading 
    st.markdown(
        """
        <p class='centered-text' style='font-size: 1.1rem; font-weight: 400;'>
        From global mass balance trends to the vanishing ice of Italy and South Tyrol<br>
        explore how glaciers have retreated over the last century</p>
        """, 
        unsafe_allow_html=True
    )
    
    # 4. Interactive Stat Cards (Native Streamlit Column Buttons)
    st.markdown("<br>", unsafe_allow_html=True)
    card_col1, card_col2, card_col3 = st.columns(3)
    
    # World Card Button
    with card_col1:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-size: 2rem;'>🌐</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin: 0;'>World</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 0.9rem; min-height: 50px;'>Global glacier mass balance from 1976 to 2025 across 20 world regions.</p>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; margin-bottom: 0.8rem;'><span style='font-size: 0.75rem; padding: 3px 10px; border-radius: 99px; border: 1px solid #ABC6DE;'>WGMS · 50 years</span></div>", unsafe_allow_html=True)
            if st.button("Explore World Data →", key="btn_world", use_container_width=True, type="primary"):
                st.session_state.current_page = "World"
                st.rerun()

    # Italy Card Button
    with card_col2:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-size: 2rem;'>🇮🇹</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin: 0;'>Italy</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 0.9rem; min-height: 50px;'>900+ glaciers across Italian mountain sectors, comparing three inventories since 1925.</p>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; margin-bottom: 0.8rem;'><span style='font-size: 0.75rem; padding: 3px 10px; border-radius: 99px; border: 1px solid #ABC6DE;'>New Italian Glacier Inventory</span></div>", unsafe_allow_html=True)
            if st.button("Explore Italy Data →", key="btn_italy", use_container_width=True, type="primary"):
                st.session_state.current_page = "Italy"
                st.rerun()

    # South Tyrol Card Button
    with card_col3:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; font-size: 2rem;'>🏔️</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin: 0;'>South Tyrol</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 0.9rem; min-height: 50px;'>Homogenized glacier polygons across 1997, 2005, and 2017 — area loss by mountain range.</p>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; margin-bottom: 0.8rem;'><span style='font-size: 0.75rem; padding: 3px 10px; border-radius: 99px; border: 1px solid #ABC6DE;'>Galos et al. 2023</span></div>", unsafe_allow_html=True)
            if st.button("Explore South Tyrol Data →", key="btn_st", use_container_width=True, type="primary"):
                st.session_state.current_page = "South Tyrol"
                st.rerun()

    # 5. Global Trend Chart Section
    df = pd.read_csv("data/wgms-amce-2026-02-10/global.csv")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["gt_cumsum"],
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(55, 138, 221, 0.15)",
        line=dict(color="#378ADD", width=2),
        hovertemplate="%{x}: %{y:.0f} Gt<extra></extra>"
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showticklabels=True, tickfont=dict(size=15)),
        yaxis=dict(showgrid=False, showticklabels=False),
        showlegend=False,
    )

    with st.container():
        st.markdown("<br><br> <h5 style='text-align: center;'> 🧊 Cumulative global ice mass change (1976–2025)</h5>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # 6. Image comparison
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<h5 style='text-align: center;'>Visual Evidence: Glacier Retreat Over Time</h5>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Drag the slider handle to compare 1863 against 2018.</p>", unsafe_allow_html=True)
        
        # We use equal spacer weights on the left and right (e.g., 1 and 1)
        # and a large number in the middle (e.g., 8).
        # This squeezes the column boundaries tightly from both sides, 
        # leaving NO room for the slider to sit off-center.
        _, center_layout_space, _ = st.columns([1.4, 7.2, 1.4])

        with center_layout_space:
            image_comparison(
                img1="imgs/Valle_Aurina_1863.jpeg", 
                img2="imgs/Valle_Aurina_2018.jpeg",     
                label1="Valle Aurina 1863",                   
                label2="Valle Aurina 2018",                   
                starting_position=50,                        
                show_labels=True,                            
                make_responsive=True, 
            )

# --- INNER PAGE ROUTING (Loads your secondary files) ---
elif st.session_state.current_page == "World":
    exec(open("pages/1_World.py").read())

elif st.session_state.current_page == "Italy":
    exec(open("pages/2_Italy.py").read())

elif st.session_state.current_page == "South Tyrol":
    exec(open("pages/3_South_Tyrol.py").read())