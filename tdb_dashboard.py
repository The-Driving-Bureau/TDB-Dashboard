import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.markdown(
    """
    <style>
    body {
        background-color: #f9f9f9;
    }
    .css-18e3th9 {
        background-color: #fff;
        border: 1px solid #eaeaea;
        border-radius: 10px;
        padding: 20px;
    }
    .st-bx {
        background-color: #f0f3f7;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    h1, h2, h3, .stText, .stMarkdown {
        color: #003057;
    }
    .stButton>button {
        background-color: #0072ce;
        color: white;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load crash data from CSV
df = pd.read_csv("crash_data.csv")

# Add filter for county
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
st.subheader("Work Zone Crash Involvement")
st.write(filtered_df["Work Zone Crash"].value_counts())

st.subheader("Motorcycle Crash Involvement")
st.write(filtered_df["Motorcycle Crash"].value_counts())

st.subheader("Unrestrained Occupants")
st.write(filtered_df["Unrestrained Occupants"].value_counts())