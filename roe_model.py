
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import os
import time

# Wide mode
st.set_page_config(layout="wide")

# -------------------- READ FILE --------------------
# Check if file exists. Throws error if file is not present

data_file = "app_tracker.xlsx"

if os.path.exists(data_file):
    df = pd.read_excel(data_file)
    st.success("Data loaded from master file.")
else:
    alert = st.warning("Master data file not found. Example data is loaded below.")
    data_file = "example_app_tracker.xlsx"

apps = pd.read_excel(data_file, sheet_name="Tracker")
calc = pd.read_excel(data_file, sheet_name="Data Calculations")
roe = pd.read_excel(data_file, sheet_name="ROE Calculation")
dash = pd.read_excel(data_file, sheet_name="Dashboard")

# -------------------- CONSTANTS --------------------

# Example custom colors for each status
status_order = dash["Status"].dropna()
custom_colors = ["#d8c0c0", "#db9abc", "#d24d7c", "#98A4EB", "#5c7579", "#d59287", "#4db7cf", "#0d9937"]

# Calculate response rate
total_apps = dash["# In Status"].sum()
valid_responses = ["Interviewing", "Denied", "Rejected", "Offer"]
response_rate = sum(1 for app_stat in apps["Status"].dropna() if app_stat in valid_responses)
num_interviews = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing", "Rejected"])
current_interviews = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing"])
sum_interviews = apps["Number of Interviews"].sum()
unique_companies = len(pd.unique(apps['Company']))

# -------------------- FUNCTIONS --------------------

# Takes the Excel structure I have and makes the Excel sheet data chartable
def convert_to_st(df: pd.DataFrame, x: str, y: str):
    x_side = df[x].dropna().astype(int)
    y_side = df[y][0:len(x_side)]
    new_df = pd.DataFrame({
        x: x_side.values,
        y: y_side.values
    })
    return new_df

# -------------------- HEADER --------------------
st.title("Job Application - Data Visualization")

# Layer 1 Columns
st.header("Graham Harris")
st.text("Since being laid off in April 2025, I've been hard at work applying to new roles. This project is a culmination of all of the data I've collected, to showcase my data visualization skills.")
st.text("Example data is loaded on the public Github repo - please ask for the master data source.")
st.write("#")

st.subheader("General Application Information")


# -------------------- COLUMN 1 --------------------

col1, col2, col3 = st.columns(3)
with col1:
    st.text("Applications by industry:")
    industry_df = convert_to_st(calc, "Number of Companies", "Industry")
    # They're backwards here, gotta swap
    industry_df = industry_df.reindex(columns=["Industry", "Number of Companies"])
    industry_df.reset_index(drop=True, inplace=True)
    # Display the DataFrame
    st.dataframe(industry_df, hide_index=True)

# Apps Per Week
with col2:
    st.text("Applications per week:")
    weekly_df = convert_to_st(calc, "Week Number", "Apps Per Week")
    # Create the chart
    weekly = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("Week Number:O", title="Week"),
        y=alt.Y("Apps Per Week:Q", title="Applications")
    )
    st.altair_chart(weekly, use_container_width=True)

# Metrics
with col3:
    matrix1, matrix2, matrix3 = st.columns(3)
    with matrix1:
        rate = str('{0:.4g}'.format((response_rate/total_apps)*100)) + "%"
        st.metric("Response Rate:", rate)
        traction_rate = str('{0:.3g}'.format((current_interviews/total_apps)*100)) + "%"
        st.metric("Traction Rate:", traction_rate)
        st.metric("Unique companies:", unique_companies)
    with matrix2:
        st.metric("Roles interviewed for:", num_interviews)
        st.metric("Total sum of interviews:", sum_interviews)
    with matrix3:
        st.write("#")

# -------------------- COLUMN 2 --------------------
next1, next2, next3 = st.columns(3)

with next1:
    st.text(" ")
    st.text(" ")
    st.text(" ")
    st.text(" ")
    st.text("For more information, my resume, or to see the original data set, please email me at grahamh1019@gmail.com. Looking forward to hearing from you!")

with next2:
    st.text("Applications by platform:")
    platform_df = convert_to_st(dash, "Platform Applications", "Platform")
    print(dash)
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Platform:O", title="Platform", sort=None),
        y=alt.Y("Platform Applications:Q", title="# Applications Sent")
    )
    st.altair_chart(platform, use_container_width=True)

with next3:
    st.text("Applications by role:")
    platform_df = convert_to_st(dash, "Count", "Role Type")
    print(dash)
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type", sort=None),
        y=alt.Y("Count:Q", title="# Applied To")
    )
    st.altair_chart(platform, use_container_width=True)

# -------------------- APP DATA --------------------

st.write("#")
st.subheader("Return on Effort")

# Scatterplot colored by application status
roe_formatted = roe.reset_index().rename(columns={"index": "Application Number"})
roe_formatted = roe_formatted.drop([21, 67])
scatter = alt.Chart(roe_formatted).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("Return on Effort:Q", title="Return on Effort"),
    color=alt.Color("Application Status:N", 
                title="Status", 
                scale=alt.Scale(domain=status_order, range=custom_colors)),
    tooltip=["Application Number", "Company Name", "Application Status", "Return on Effort"]
)
scatterplot = st.altair_chart(scatter, use_container_width=True)

more1, more2 = st.columns(2)

with more1:
    st.text("""This is a measure of "return on effort" or how much theoretical effort it should take for me to get the job. Each point is measured by estimating effort for each: platform, role type, and salary likelihood.""")

    st.text("Note: Applications 21 and 67 are dropped in the scatterplot because they are extreme outliers.")
    
with more2:
    # Status
    status_df = convert_to_st(dash, "# In Status", "Status")
    status = alt.Chart(status_df).mark_bar().encode(
        x=alt.X("Status:O", title="Status", sort=None),
        y=alt.Y("# In Status:Q", title="# In Status"),
        color=alt.Color("Status:N", 
                title="Status", 
                scale=alt.Scale(domain=status_order, range=custom_colors))
    )
    st.altair_chart(status, use_container_width=True)
