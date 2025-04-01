import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("TDB Crash Risk Snapshot")

df = pd.read_csv("dmv_freight_crash_sample.csv")
df["CRASH_DATE"] = pd.to_datetime(df["CRASH_DATE"])
df["HOUR"] = df["CRASH_DATE"].dt.hour

state = st.selectbox("Select a State", df["STATE"].unique())
filtered = df[df["STATE"] == state]

vehicle_types = filtered["VEHICLE_TYPE"].unique()
selected_vehicle = st.selectbox("Filter by Vehicle Type", vehicle_types)
filtered = filtered[filtered["VEHICLE_TYPE"] == selected_vehicle]

crash_types = filtered["CRASH_TYPE"].unique()
selected_crash = st.selectbox("Filter by Crash Type", crash_types)
filtered = filtered[filtered["CRASH_TYPE"] == selected_crash]

st.subheader("Crashes by Hour of Day")
hour_data = filtered["HOUR"].value_counts().sort_index()
fig, ax = plt.subplots()
ax.bar(hour_data.index, hour_data.values, color='skyblue')
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Number of Crashes")
st.pyplot(fig)

st.subheader("Crash Density Heatmap")
st.map(filtered[["LATITUDE", "LONGITUDE"]].dropna())

st.info("🚀 Want a custom crash risk report? Fill out the form [here](https://forms.gle/your-google-form)")