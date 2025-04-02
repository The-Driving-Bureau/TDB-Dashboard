import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.image("logo.png", width=200)
st.markdown("## Welcome to The Driving Bureau Crash Risk Dashboard")

# Load crash data from CSV
df = pd.read_csv("crash_data.csv")

# Add filter for county
with st.sidebar:
    st.title("Filter Panel")
    counties = df["Crash County Description"].dropna().unique()
    selected_counties = st.multiselect("Select Counties", sorted(counties), default=list(counties))
filtered_df = df[df["Crash County Description"].isin(selected_counties)]

# Show bar chart of crashes by impact type
st.subheader(f"Crashes by Impact Type in {', '.join(selected_counties)}")
impact_counts = filtered_df["CollisionImpact Description"].value_counts()

fig, ax = plt.subplots()
ax.bar(impact_counts.index, impact_counts.values, color="orange")
ax.set_xlabel("Impact Type")
ax.set_ylabel("Number of Crashes")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Show breakdown by crash involvement
col1, col2 = st.columns(2)

with col1:
    st.subheader("Work Zone Crash Involvement")
    st.write(filtered_df["Work Zone Crash"].value_counts())

    st.subheader("Unrestrained Occupants")
    st.write(filtered_df["Unrestrained Occupants"].value_counts())

with col2:
    st.subheader("Motorcycle Crash Involvement")
    st.write(filtered_df["Motorcycle Crash"].value_counts())

with st.expander("View Raw Crash Data"):
    st.dataframe(filtered_df)