import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("TDB Crash Risk Snapshot")

df = pd.read_csv("crash_data.csv")

state = st.selectbox("Select a State", df["STATE"].unique())
filtered = df[df["STATE"] == state]

st.subheader("Crashes by Time of Day")
hour_data = filtered["HOUR"].value_counts().sort_index()
st.bar_chart(hour_data)

st.info("🚀 Want a custom crash risk report? Fill out the form [here](https://forms.gle/your-google-form)")