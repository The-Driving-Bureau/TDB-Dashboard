import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load crash data from CSV
df = pd.read_csv("crash_data.csv")

# Add filter for county
counties = df["Crash County Description"].dropna().unique()
selected_county = st.selectbox("Select a County", sorted(counties))
filtered_df = df[df["Crash County Description"] == selected_county]

# Show bar chart of crashes by impact type
st.subheader(f"Crashes by Impact Type in {selected_county}")
impact_counts = filtered_df["CollisionImpact Description"].value_counts()

fig, ax = plt.subplots()
ax.bar(impact_counts.index, impact_counts.values, color="orange")
ax.set_xlabel("Impact Type")
ax.set_ylabel("Number of Crashes")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Show breakdown by crash involvement
st.subheader("Work Zone Crash Involvement")
st.write(filtered_df["Work Zone Crash"].value_counts())

st.subheader("Motorcycle Crash Involvement")
st.write(filtered_df["Motorcycle Crash"].value_counts())

st.subheader("Unrestrained Occupants")
st.write(filtered_df["Unrestrained Occupants"].value_counts())