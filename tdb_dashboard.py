import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

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

filtered_df = df[
    (df["Crash County Description"].isin(selected_counties)) &
    (df["Crash Severity Description"].isin(selected_severities)) &
    (df["Crashhour"].between(selected_hours[0], selected_hours[1]))
]

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