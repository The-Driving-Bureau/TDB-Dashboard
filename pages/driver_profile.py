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
    print("DEBUG - User Info Response:", user_info)
    user_data = user_info.get("user", user_info)
    driver_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
    driver_email = user_data.get("email", "N/A")
    driver_phone = user_data.get("phone", "N/A")
    driver_timezone = user_data.get("time_zone", "N/A")

    # Extract nested company role if available
    role = user_data.get("company_connection", {}).get("role", user_data.get("role", "Driver"))
    status = user_data.get("company_connection", {}).get("status", "Unknown")

    # Replace fallback values with actual API data
    distance_driven = user_data.get('distance_driven') or "🚧 Data not available"
    deliveries_count = user_data.get('deliveries', {}).get('count') or "🚧 Data not available"
    experience_level = user_data.get('experience', {}).get('level') or "🚧 Data not available"
    rating_value = user_data.get('performance', {}).get('rating', 4)
    rating = "⭐" * int(rating_value) + "☆" * (5 - int(rating_value))
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
st.title("🚗 Driver Profile Dashboard")

st.subheader("👤 Driver Information")
with st.container():
    left_col, right_col = st.columns([2, 1], gap="large")
    with left_col:
        driver_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        st.markdown(f"### {driver_name or 'N/A'}")
        st.image("https://via.placeholder.com/100", caption="Driver Photo", width=100)
        st.markdown(f"**Role:** {role}")
        st.markdown(f"**Status:** {status}")

        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Miles Driven", distance_driven)
            st.markdown(f"**Experience:** {experience_level}")
        with info_col2:
            st.metric("Deliveries", deliveries_count)
            st.markdown(f"**Rating:** {rating}")
        with info_col3:
            st.markdown("**Contact:**")
            st.markdown(f"[📧 Email](mailto:{driver_email})")
            st.markdown(f"📞 {driver_phone}")
            st.markdown(f"🕓 Time Zone: {driver_timezone}")

    with right_col:
        st.subheader("🛡️ Performance Chart")
        radar_data = pd.DataFrame(dict(
            r=[85, 92, 88, 90, 87],
            theta=["Speed", "Compliance", "Success Rate", "Customer Service", "Reliability"]
        ))
        fig_radar = px.line_polar(radar_data, r='r', theta='theta', line_close=True)
        fig_radar.update_traces(fill='toself')
        st.plotly_chart(fig_radar, use_container_width=True)

st.subheader("📊 Driver Summary Overview")

# Placeholder metrics (to be replaced with API data later)
weekly_miles = 450
weekly_delta = 15
hos_compliance = 93
hos_delta = 2
avg_speed = 56

# Placeholder chart data
miles_data = pd.DataFrame({
    "Date": pd.date_range(start="2024-04-01", periods=7, freq="D"),
    "Miles": [60, 75, 80, 55, 90, 40, 50]
})
fig_miles = px.bar(miles_data, x="Date", y="Miles", title="Miles Driven per Day")

hos_data = pd.DataFrame({
    "Date": pd.date_range(start="2024-04-01", periods=7, freq="D"),
    "Compliance (%)": [92, 95, 88, 90, 94, 91, 93]
})
fig_hos = px.line(hos_data, x="Date", y="Compliance (%)", title="Daily HOS Compliance")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Miles", "HOS", "Speed"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Miles This Week", f"{weekly_miles} mi", delta=f"{weekly_delta} mi")
    with col2:
        st.metric("HOS Compliance", f"{hos_compliance}%", delta=f"{hos_delta}%")
    with col3:
        st.metric("Avg Speed", f"{avg_speed} mph")

with tab2:
    st.metric("Miles This Week", f"{weekly_miles} mi", delta=f"{weekly_delta} mi")
    st.plotly_chart(fig_miles, use_container_width=True)

with tab3:
    st.metric("HOS Compliance", f"{hos_compliance}%", delta=f"{hos_delta}%")
    st.plotly_chart(fig_hos, use_container_width=True)

with tab4:
    st.metric("Avg Speed", f"{avg_speed} mph")
    st.markdown("Speed trends will be visualized here soon.")