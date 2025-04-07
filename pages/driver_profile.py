import streamlit as st
import pandas as pd
import plotly.express as px
import shapely
import polyline
import requests
from gomotive.auth import get_gomotive_access_token
from gomotive.api import get_user_info, get_driver_by_id
from gomotive.session import save_token_to_session, get_token_from_session, is_token_expired

st.set_page_config(page_title="Driver Profile", layout="wide", initial_sidebar_state="collapsed")
with st.container():
    st.markdown("""<div style='position:sticky;top:0;background:#f9f9f9;padding:10px 0;z-index:100;border-bottom:1px solid #ddd;'>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Home"):
            st.switch_page("tdb_dashboard.py")  # Only works if using multipage app launcher
    with col2:
        if st.button("Driver Profile"):
            pass  # Already on the profile
    with col3:
        if st.button("Settings"):
            st.warning("Settings not implemented yet.")
    st.markdown("""</div>""", unsafe_allow_html=True)

st.subheader("👤 GoMotive User Info")
access_token = get_token_from_session()

if not access_token or is_token_expired():
    auth_code = st.text_input("Enter your authorization code:", type="password")
    if auth_code:
        try:
            token_data = get_gomotive_access_token(auth_code)
            save_token_to_session(token_data)
            access_token = token_data.get("access_token")
            st.success("✅ Successfully retrieved GoMotive API token.")
            st.code(f"Access Token: {access_token[:10]}... (truncated)", language="text")
        except Exception as e:
            import traceback
            st.error(f"❌ Failed to retrieve GoMotive API token: {e}")
            with st.expander("🪵 Debug Log", expanded=False):
                st.code(traceback.format_exc(), language="python")
            st.stop()

if not access_token:
    st.warning("Please enter a valid authorization code to continue.")
    st.stop()

driver_response = get_user_info(access_token)
demo_driver_ids = [
    {"id": str(user["user"]["id"]), "name": f'{user["user"]["first_name"]} {user["user"]["last_name"]}'}
    for user in driver_response.get("users", [])
]

driver_names = [f"{d['name']} (ID: {d['id']})" for d in demo_driver_ids]
selected_driver = st.selectbox("Select a driver to view:", driver_names)

selected_id = selected_driver.split("ID: ")[-1].replace(")", "").strip()

try:
    user_info = get_driver_by_id(selected_id, access_token)
    driver_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
    driver_email = user_info.get("email", "N/A")
    driver_phone = user_info.get("phone", "N/A")
    driver_timezone = user_info.get("time_zone", "N/A")

    # Extract nested company role if available
    role = user_info.get('company_connection', {}).get('role', user_info.get('role', 'Driver'))
    status = user_info.get('company_connection', {}).get('status', 'Unknown')

    # Simulate fallback values for now
    distance_driven = user_info.get('distance_driven', '🚧 Data not available')
    deliveries_count = user_info.get('deliveries_count', '🚧 Data not available')
    experience_level = user_info.get('experience_level', '🚧 Data not available')
    rating = user_info.get('rating', '⭐⭐⭐⭐☆')
except Exception as e:
    st.error(f"❌ Failed to retrieve GoMotive API token or user info: {e}")
    with st.expander("🪵 Debug Log", expanded=True):
        import traceback
        st.code(traceback.format_exc(), language="python")
    st.stop()

with st.expander("🔍 API Call Log", expanded=False):
    st.code("Requesting user info from: https://api.gomotive.com/v1/users/{driver_id}", language="text")
    st.code(f"Authorization: Bearer {access_token[:10]}... (truncated)", language="text")
    st.code(f"Response: {user_info}", language="json")

st.markdown(f"### {driver_name or 'N/A'}")
st.markdown(f"**Role:** {role}")
st.markdown(f"**Status:** {status}")
st.markdown(f"**Miles Driven:** {distance_driven}")
st.markdown(f"**Deliveries:** {deliveries_count}")
st.markdown(f"**Rating:** {rating}")
st.markdown(f"**Experience:** {experience_level}")
st.markdown("**Contact:**")
st.markdown(f"[📧 Email](mailto:{driver_email})")
st.markdown(f"📞 {driver_phone}")
st.markdown(f"🕓 Time Zone: {driver_timezone}")

st.markdown("## 📂 Navigation")
nav_selection = st.selectbox(
    "Navigate to:",
    options=["Driver Profile", "Overview", "Settings"],
    index=0
)

if nav_selection != "Driver Profile":
    st.warning(f"'{nav_selection}' page is under construction.")
    st.stop()

st.title("🚗 Driver Profile Dashboard")

st.subheader("👤 Driver Information")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=120)
with col2:
    st.markdown(f"### {driver_name or 'N/A'}")
    st.markdown(f"**Role:** {role}")
    st.markdown(f"**Status:** {status}")
    st.markdown(f"**Miles Driven:** {distance_driven}")
    st.markdown(f"**Deliveries:** {deliveries_count}")
    st.markdown(f"**Rating:** {rating}")
    st.markdown(f"**Experience:** {experience_level}")
    st.markdown("**Contact:**")
    st.markdown(f"[📧 Email](mailto:{driver_email})")
    st.markdown(f"📞 {driver_phone}")
    st.markdown(f"🕓 Time Zone: {driver_timezone}")

col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("📊 Top Performer Comparison")
    performer_data = pd.DataFrame({
        "Member": ["Brian", "Nick", "Tim", "Tom"],
        "Earnings": [1345, 950, 1140, 665],
        "Cases": [124, 80, 92, 60],
        "Rate": [0.87, 0.91, 0.88, 0.85]
    })
    st.dataframe(performer_data)

    st.subheader("📈 Synergy Report")
    synergy_data = pd.DataFrame({
        "Date": pd.date_range(start="2024-01-01", periods=12, freq="M"),
        "Score": [88, 91, 85, 87, 90, 92, 93, 91, 89, 94, 95, 96]
    })
    fig = px.line(synergy_data, x="Date", y="Score", markers=True, title="Monthly Synergy Score")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🛡️ Performance Chart")
    radar_data = pd.DataFrame(dict(
        r=[85, 92, 88, 90, 87],
        theta=["Speed", "Compliance", "Success Rate", "Customer Service", "Reliability"]
    ))
    fig_radar = px.line_polar(radar_data, r='r', theta='theta', line_close=True)
    fig_radar.update_traces(fill='toself')
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("📋 Task Feed")
    st.markdown("""
    - ✅ Present 2024 Year-End Safety Stats (Company)
    - 🕐 Hold Interview for Safety Officer Role (Hiring)
    - 📌 Incident Resolution Follow-Up (Pending)
    - 🧾 Prepare Agreement with Insurance Partner (In Progress)
    - ❌ Update GPS Route Tracker (Overdue)
    """)