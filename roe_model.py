
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
    st.success("Success: Data loaded from master file.")
else:
    alert = st.warning("Note: Example data is loaded below.")
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
valid_responses = ["Interviewing", "Denied", "Rejected", "Offer", "Ghosted"]
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
st.text("Example data is loaded on the public application - please ask for the master data source to see my actual application journey.")

# -------------------- TABLE OF CONTENTS --------------------

# INCLUDE A TABLE OF CONTENTS with a href="#hashtag"

# -------------------- COLUMN 1 --------------------
st.write("#")
st.html("<hr>")
st.header("Raw Data")

col1, col2, col3 = st.columns(3)
with col1:
    st.text("Applications by industry:")
    industry_df = convert_to_st(calc, "Number of Companies", "Industry")
    # They're backwards here, gotta swap
    industry_df = industry_df.reindex(columns=["Industry", "Number of Companies"])
    industry_df.reset_index(drop=True, inplace=True)
    # Display the DataFrame
    st.dataframe(industry_df, hide_index=True)

# Metrics
with col2:
    matrix1, matrix2 = st.columns(2)
    with matrix1:
        rate = str('{0:.4g}'.format((response_rate/total_apps)*100)) + "%"
        st.metric("Response Rate:", rate)
        traction_rate = str('{0:.3g}'.format((current_interviews/total_apps)*100)) + "%"
        st.metric("Traction Rate:", traction_rate)
        st.metric("Number of unique companies:", unique_companies)
    with matrix2:
        st.metric("Number of roles interviewed for:", num_interviews)
        st.metric("All-time interviews:", sum_interviews)

# Apps Per Week
with col3:
    st.text("For more information, my resume, or to see the original data set, please email me at grahamh1019@gmail.com. Looking forward to hearing from you!")

# -------------------- COLUMN 2 --------------------
st.html("<hr>")
st.write("#")
st.header("Application Breakdown")

next1, next2, next3 = st.columns(3)

with next1:
    st.text("Applications per week:")
    weekly_df = convert_to_st(calc, "Week Number", "Apps Per Week")
    # Create the chart
    weekly = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("Week Number:O", title="Week"),
        y=alt.Y("Apps Per Week:Q", title="Applications"),
        color=alt.value("#db9abc")
    )
    st.altair_chart(weekly, use_container_width=True)

with next2:
    st.text("Applications by platform:")
    platform_df = convert_to_st(dash, "Platform Applications", "Platform")
    print(dash)
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Platform:O", title="Platform", sort=None),
        y=alt.Y("Platform Applications:Q", title="# Applications Sent"),
        color=alt.value("#d59287")
    )
    st.altair_chart(platform, use_container_width=True)

    # Interviews Per Week
    # --- Clean and prepare the data ---
    apps['Week'] = pd.to_numeric(apps['Week'], errors='coerce').fillna(0).astype(int)
    apps['Number of Interviews'] = pd.to_numeric(apps['Number of Interviews'], errors='coerce').fillna(0).astype(int)
    # --- Get all positive week numbers in range ---
    all_weeks = pd.DataFrame({'Week': range(apps['Week'].min(), apps['Week'].max() + 1)})
    all_weeks = all_weeks[all_weeks['Week'] > 0]
    # --- Group by Week and sum Number of Interviews ---
    interviews_per_week = (
        apps.groupby('Week')['Number of Interviews']
        .sum()
        .reset_index(name='Interviews')
    )
    # --- Merge with full week list to fill in missing weeks with 0 ---
    interviews_per_week = pd.merge(all_weeks, interviews_per_week, on='Week', how='left').fillna(0)
    interviews_per_week['Interviews'] = interviews_per_week['Interviews'].astype(int)
    # --- Plot using Altair ---
    st.text("Interviews by week applied:")
    chart = alt.Chart(interviews_per_week).mark_bar().encode(
        x=alt.X('Week:O', title='Week Number'),
        y=alt.Y('Interviews:Q', title='Total Interviews'),
        tooltip=['Week', 'Interviews'],
        color=alt.value("#5c7579")
    )
    st.altair_chart(chart, use_container_width=True)
    st.text("Note: This chart shows the number of interviews per week based on when the application was sent, not when the actual interview occured.")

with next3:
    st.text("Applications by role:")
    platform_df = convert_to_st(dash, "Count", "Role Type")
    print(dash)
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type", sort=None),
        y=alt.Y("Count:Q", title="# Applied To"),
        color=alt.value("#98A4EB")
    )
    st.altair_chart(platform, use_container_width=True)

# -------------------- ROE DATA --------------------
st.html("<hr>")
st.write("#")
st.header("Return on Effort")

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
    st.subheader("'Return on Effort' Definition")
    st.text("""This is a measure of "return on effort" or how much theoretical effort it should take for me to get the job. High values indicate that I should be an ideal applicant to the position. Low values indicate that it might be a stretch for me to get the job. Each point is measured by estimating the effort for each: platform, role type, and salary likelihood.""")
    st.text("Notes about the data:")
    st.html(
        "<ol style='padding-left: 5%'>" \
        "<li>Applications 21 and 67 are dropped in the scatterplot because they are extreme outliers in the master data.</li>" \
        "<li>Roles that have a '0' ROE did not have a salary listed on the job posting.</li>" \
        "</ol>"
    )
    
with more2:
    # Status total
    st.text("Applications by status:")
    status_df = convert_to_st(dash, "# In Status", "Status")
    status = alt.Chart(status_df).mark_bar().encode(
        x=alt.X("Status:O", title="Status", sort=None),
        y=alt.Y("# In Status:Q", title="# In Status"),
        color=alt.Color("Status:N", 
                title="Status", 
                scale=alt.Scale(domain=status_order, range=custom_colors))
    )
    st.altair_chart(status, use_container_width=True)

    

# -------------------- INSIGHTS --------------------
st.html("<hr>")
st.write("#")
c1, c2, c3 = st.columns([1, 6, 1])  # Adjust ratios to control padding

with c2:
    st.header("Insights (Work In Progress)")
    st.text("Note: These points are personal to my application journey and may not be true of the total application landscape.")
    st.html(
        "<ul style='padding-left: 5%'>" \
        "<li>The most active hiring markets have been in marketing, AI, and data analytics.</li>" \
        "<li>Companies average 3-5 interviews throughout the process. Generally the pattern is: 1) recruiter call, 2) hiring manager interview, 3) case study assessment, 4) final behavioral check.</li>" \
        "<li>Referrals have generally not been helpful.</li>" \
        "<li>Workday is a repetitve platform for applicants - large companies ask applicants to create an account and manually add information, which is time-consuming.</li>" \
        "</ul>"
    )

