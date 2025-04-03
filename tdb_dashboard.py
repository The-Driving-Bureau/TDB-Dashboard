import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import polyline
from shapely.geometry import Point, LineString

st.image("logo.png", width=200)
st.markdown("## Welcome to The Driving Bureau Crash Risk Dashboard")

# Load crash data from CSV
df = pd.read_csv("crash_data.csv")

# Add filter for county
with st.sidebar:
    st.title("Filter Panel")
    counties = df["Crash County Description"].dropna().unique()
    selected_counties = st.multiselect("Select Counties", sorted(counties), default=list(counties))

    severities = df["Crash Severity Description"].dropna().unique()
    selected_severities = st.multiselect("Select Severity Types", sorted(severities), default=list(severities))

    hours = sorted(df["Crashhour"].dropna().unique())
    selected_hours = st.slider("Select Hour Range", min_value=min(hours), max_value=max(hours), value=(min(hours), max(hours)))

st.subheader("🚚 Route Risk Preview (Mapbox)")

travel_hours = st.slider("Expected Travel Time Range (24-hour format)", min_value=0, max_value=23, value=(8, 10))

# Mapbox token
MAPBOX_TOKEN = "pk.eyJ1IjoibXJsZWU4NTAiLCJhIjoiY205MGgxdm5qMDcyODJscHE3dDNucWg1dSJ9._xEbS_Z_do2s8oaoeYdvww"

# User input for route
start = st.text_input("Start Address", "Baltimore, MD")
end = st.text_input("End Address", "Annapolis, MD")

filtered_df = df[
    (df["Crash County Description"].isin(selected_counties)) &
    (df["Crash Severity Description"].isin(selected_severities)) &
    (df["Crashhour"].between(selected_hours[0], selected_hours[1]))
]

def geocode_address(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={MAPBOX_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        coords = response.json()["features"][0]["center"]
        return coords[0], coords[1]  # lon, lat
    else:
        return None

def get_route_geometry(start_coords, end_coords):
    coords = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords}?geometries=geojson&access_token={MAPBOX_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["routes"][0]["geometry"]["coordinates"]
    else:
        return []

def calculate_route_risk(route_coords, crashes_df, travel_hours, distance_threshold=0.01):
    route_line = LineString(route_coords)
    total_score = 0
    crash_points = []
    overlapping_crashes = 0

    for _, row in crashes_df.iterrows():
        crash_point = Point(row["Longitude"], row["Latitude"])
        if route_line.distance(crash_point) < distance_threshold:
            if travel_hours[0] <= row["Crashhour"] <= travel_hours[1]:
                overlapping_crashes += 1
                base_score = 1
                if row["Crashhour"] in range(20, 24) or row["Crashhour"] in range(0, 6):
                    base_score += 1  # add 1 more point if crash occurred at night
                total_score += base_score

    # Adjust risk by overlapping density (normalized weight factor, increased to 3x)
    density_weight = overlapping_crashes * 0.6  # was 0.2, now x3
    total_score = total_score + density_weight
    return total_score, overlapping_crashes

def classify_risk_level(score, max_score=30):
    scaled_score = min(int((score / max_score) * 100), max_score)
    if scaled_score < 20:
        level = "🟢 Low"
    elif scaled_score < 50:
        level = "🟡 Moderate"
    elif scaled_score < 80:
        level = "🟠 Elevated"
    else:
        level = "🔴 High"
    return scaled_score, level

if start and end:
    start_coords = geocode_address(start)
    end_coords = geocode_address(end)
    if start_coords and end_coords:
        route_coords = get_route_geometry(start_coords, end_coords)
        route_df = pd.DataFrame(route_coords, columns=["lon", "lat"])
        st.map(route_df)
        
        if "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
            route_score, overlapping_crashes = calculate_route_risk(route_coords, df, travel_hours)
            scaled_score, risk_level = classify_risk_level(route_score)
            st.markdown(f"### 🔥 Route Risk Score: {scaled_score} ({risk_level})")
            st.caption(f"Overlapping crashes during {travel_hours[0]}:00–{travel_hours[1]}:00: {overlapping_crashes}")
            
            with st.expander("📊 How is the Route Risk Score Calculated?"):
                st.markdown(f"""
                The **Route Risk Score** estimates safety risk based on crashes that occurred during your selected travel time window.

                ### Risk Factor Used:
                - ⏱️ **Crashes during {travel_hours[0]}:00–{travel_hours[1]}:00**: +1 point each  

                Each crash that occurred within your expected travel range adds to your route score.  
                The higher the score, the more crash activity occurred along your route at that time.

                ### Risk Levels
                - 🟢 0–19: Low — minimal crash history
                - 🟡 20–49: Moderate — some crash activity
                - 🟠 50–79: Elevated — frequent crash presence
                - 🔴 80–100: High — avoid if possible

                _Use this score to evaluate route safety at your intended time of travel._
                """)
    else:
        st.warning("Unable to fetch route. Please check address spelling.")

# Add Route Risk Heatmap if Latitude/Longitude exists
if "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
    st.subheader("Route Risk Heatmap")

    # Example risk score calculation (simplified for demo)
    def calculate_risk(row):
        score = 0
        if row["Crashhour"] in range(20, 24) or row["Crashhour"] in range(0, 6):
            score += 2
        return score

    filtered_df["Risk Score"] = filtered_df.apply(calculate_risk, axis=1)

    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        size="Risk Score",
        color="Risk Score",
        color_continuous_scale="OrRd",
        mapbox_style="carto-positron",
        zoom=7,
        height=600,
        title="Crash Risk by Location"
    )

    st.plotly_chart(fig_map)
else:
    st.warning("Latitude and Longitude data is missing. Unable to generate Route Risk Heatmap.")

# Show bar chart of crashes by impact type
st.subheader(f"Crashes by Impact Type in {', '.join(selected_counties)}\nSeverity: {', '.join(selected_severities)}\nHours: {selected_hours[0]}–{selected_hours[1]}")
impact_counts = filtered_df["CollisionImpact Description"].value_counts()

# Alternative View: Horizontal Bar Chart
st.subheader("Alternative View: Horizontal Bar Chart")
impact_df = impact_counts.reset_index()
impact_df.columns = ['Impact Type', 'Count']
fig_h = px.bar(
    impact_df,
    y='Impact Type',
    x='Count',
    orientation='h',
    labels={'Impact Type': 'Impact Type', 'Count': 'Number of Crashes'},
    hover_data=['Impact Type', 'Count']
)
fig_h.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig_h)

# Stacked Bar Chart: Impact Type by Severity
st.subheader("Stacked Bar Chart: Impact Type by Severity")
pivot = filtered_df.pivot_table(index='CollisionImpact Description', columns='Crash Severity Description', aggfunc='size', fill_value=0).reset_index()
fig_s = px.bar(pivot, x='CollisionImpact Description', y=pivot.columns[1:], 
               labels={'value': 'Number of Crashes', 'variable': 'Severity'},
               title='Impact Type by Severity', barmode='stack')
st.plotly_chart(fig_s)

# Heatmap: Hour vs Impact Type
import seaborn as sns
st.subheader("Heatmap: Hour vs Impact Type")
heatmap_data = filtered_df.pivot_table(index='Crashhour', columns='CollisionImpact Description', aggfunc='size', fill_value=0)
fig_heat, ax_heat = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data, cmap="Oranges", ax=ax_heat)
ax_heat.set_xlabel("Impact Type")
ax_heat.set_ylabel("Crash Hour")
st.pyplot(fig_heat)

# New chart for crashes by severity
severity_counts = filtered_df["Crash Severity Description"].value_counts().reset_index()
severity_counts.columns = ['Severity', 'Count']
fig2 = px.bar(severity_counts, x='Severity', y='Count',
              labels={'Severity': 'Severity', 'Count': 'Number of Crashes'},
              hover_data=['Severity', 'Count'])
st.plotly_chart(fig2)

# Show breakdown by crash involvement
col1, col2 = st.columns(2)

with col1:
    st.subheader("Work Zone Crash Involvement")
    st.write(filtered_df["Work Zone Crash"].value_counts())

    st.subheader("Unrestrained Occupants")
    st.write(filtered_df["Unrestrained Occupants"].value_counts())

with col2:
    st.subheader("Motorcycle Crash Involvement")
    if "Motorcycle Crash" in filtered_df.columns:
        st.write(filtered_df["Motorcycle Crash"].value_counts())
    else:
        st.warning("Motorcycle Crash data not available in this dataset.")

with st.expander("View Raw Crash Data"):
    st.dataframe(filtered_df)