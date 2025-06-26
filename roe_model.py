
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import os
import numpy as np
from datetime import datetime

# Wide mode
st.set_page_config(layout="wide", page_title="Application Data")

# ---------------------------------------- READ FILE
# Check if file exists. Throws error if file is not present

data_file = "app_tracker.xlsx"

if os.path.exists(data_file):
    df = pd.read_excel(data_file)
    st.success("Success: Data loaded from master file.")
else:
    alert = st.warning("Note: Example data is loaded below.")
    data_file = "example_app_tracker.xlsx"

apps = pd.read_excel(data_file, sheet_name="Tracker")
roe = pd.read_excel(data_file, sheet_name="ROE Calculation")

# ---------------------------------------- CONSTANTS

# Example custom colors for each status
status_order = pd.unique(apps["Status"].dropna())
custom_colors = ["#d8c0c0", "#db9abc", "#d24d7c", "#98A4EB", "#5c7579", "#d59287", "#4db7cf", "#0d9937"]

# Calculate response rate
total_apps = apps[apps.columns[0]].count()
valid_responses = ["Interviewing", "Denied", "Rejected", "Offer", "Ghosted"]
response_rate = sum(1 for app_stat in apps["Status"].dropna() if app_stat in valid_responses)
num_interviews = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing", "Rejected"])
current_interviews = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing"])
sum_interviews = apps["Number of Interviews"].sum()
unique_companies = len(pd.unique(apps['Company']))
avg_salary = (apps['Salary Min (Thousands)'].mean() + apps['Salary Max (Thousands)'].mean()) / 2

# ---------------------------------------- FUNCTIONS

# Takes the Excel structure I have and makes the Excel sheet data chartable
def convert_to_st(df: pd.DataFrame, x: str, y: str):
    x_side = df[x].dropna().astype(int)
    y_side = df[y][0:len(x_side)]
    new_df = pd.DataFrame({
        x: x_side.values,
        y: y_side.values
    })
    return new_df

# Function that shows how much I'm worth based on salary
def likelihood(salary):
    baseline = 115
    decay_rate = 12
    min_prob = 0.30
    max_prob = 0.95
    prob = np.where(
        salary <= baseline,
        max_prob,
        min_prob + (max_prob - min_prob) * np.exp(-(salary - baseline) / decay_rate)
    )
    return prob

# ---------------------------------------- GROUP BYS
# Dataframes from the Applications page that are grouped by category

industry_df = apps.groupby('Industry').agg({
        'Status': 'count',
        'Number of Interviews': 'sum',
        'Salary Min (Thousands)': 'mean',
        'Salary Max (Thousands)': 'mean'
    }).rename(columns={
        'Status': 'Number of Applications',
        'Number of Interviews': '# Interviews',
        'Salary Min (Thousands)': 'Avg Min Salary (kUSD)',
        'Salary Max (Thousands)': 'Avg Max Salary (kUSD)'
    }).reset_index().sort_values("Number of Applications", ascending=False)

role_df = apps.groupby('Role Type').agg({
        'Status': 'count',
        'Number of Interviews': 'sum',
        'Salary Min (Thousands)': 'mean',
        'Salary Max (Thousands)': 'mean'
    }).rename(columns={
        'Status': 'Number of Applications',
        'Number of Interviews': '# Interviews',
        'Salary Min (Thousands)': 'Avg Min Salary (kUSD)',
        'Salary Max (Thousands)': 'Avg Max Salary (kUSD)'
    }).reset_index().sort_values("Number of Applications", ascending=False)

weekly_df = apps.groupby('Week').agg({
        'Status': 'count',
        'Number of Interviews': 'sum'
    }).rename(columns={
        'Status': 'Applications Per Week'
    }).reset_index().sort_values("Week", ascending=False)
weekly_df = weekly_df.drop(0) # Drop the -14 values
last_four_weeks = weekly_df['Applications Per Week'].head(4).sum()

platform_df = apps.groupby('Platform').agg({
        'Status': 'count',
    }).rename(columns={
        'Status': 'Applications Per Platform'
    }).reset_index().sort_values("Applications Per Platform", ascending=False)

status_df = apps.groupby('Status').agg({
        'Role Type': 'count',
    }).rename(columns={
        'Role Type': 'Applications In Status'
    }).reset_index().sort_values("Applications In Status", ascending=False)

# ---------------------------------------- HEADER

st.title("Job Application - Data Visualization")

# Layer 1 Columns
st.header("Graham Harris")
st.text("Since I was laid off in April 2025, I've been hard at work applying to new roles. This project is a capstone project of all of the data I've collected showcasing my data visualization skills.")
st.text("Example data is loaded on the public application - please ask for the master data source to see my actual application journey.")

# ---------------------------------------- CONTENTS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Table of Contents")
st.html(
    "<ol style='padding-left: 5%;'>"
        "<li><a href='#data-aggregations'>Data Aggregations</a></li>"
        "<li><a href='#application-breakdown'>Application Breakdown</a></li>"
        "<li><a href='#interviews'>Interviews</a></li>"
        "<li><a href='#return-on-effort'>Return on Effort</a></li>"
        "<li><a href='#insights'>Insights</a></li>"
    "</ol>"
)

# ---------------------------------------- DATA AGG
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Data Aggregations")

col1, col2 = st.columns(2)
with col1:
    st.text("Applications grouped by INDUSTRY:")
    # Display the DataFrame
    st.dataframe(industry_df, hide_index=True)

# Metrics
with col2:
    st.text("Applications grouped by ROLE TYPE:")
    # Display the DataFrame
    st.dataframe(role_df, hide_index=True)

st.subheader("Metrics")
matrix1, matrix2 = st.columns(2)
with matrix1:
    rate = str('{0:.4g}'.format((response_rate/total_apps)*100)) + "%"
    st.metric("Response Rate:", rate)
    st.metric("Total number of applications:", total_apps)
    st.metric("Number of unique companies:", unique_companies)
with matrix2:
    traction_rate = str('{0:.3g}'.format((current_interviews/last_four_weeks)*100)) + "%"
    st.metric("Current traction (% interviews from applications in the last 4 weeks):", traction_rate)
    st.metric("Number of roles interviewed for:", num_interviews)
    st.metric("All-time interviews:", sum_interviews)
st.text("For more information, my resume, or to see the original data set, please email me at grahamh1019@gmail.com. Looking forward to hearing from you!")

# ---------------------------------------- APP DATA
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Application Breakdown")

next1, next2, next3 = st.columns(3)

with next1:
    st.text("Applications per WEEK:")
    # Create the chart
    weekly = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("Week:O", title="Week Number"),
        y=alt.Y("Applications Per Week:Q", title="Applications"),
        color=alt.value("#db9abc")
    )
    st.altair_chart(weekly, use_container_width=True)

with next2:
    st.text("Applications per PLATFORM:")
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Platform:O", title="Platform", sort=None),
        y=alt.Y("Applications Per Platform:Q", title="# Applications Sent"),
        color=alt.value("#d59287")
    )
    st.altair_chart(platform, use_container_width=True)

    st.text("Interviews by Week Applied:")
    chart = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X('Week:O', title='Week Number'),
        y=alt.Y('Number of Interviews:Q', title='Total Interviews'),
        tooltip=['Week', 'Number of Interviews'],
        color=alt.value("#5c7579")
    )
    st.altair_chart(chart, use_container_width=True)
    st.text("Note: This chart shows the number of interviews per week based on when the application was sent, not when the actual interview occured.")

with next3:
    st.text("Applications by role:")
    # Create the chart
    platform = alt.Chart(role_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type", sort=None),
        y=alt.Y("Number of Applications:Q", title="# Applied To"),
        color=alt.value("#98A4EB")
    )
    st.altair_chart(platform, use_container_width=True)

# ---------------------------------------- INTERVIEWS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Interviews")

if data_file == "app_tracker.xlsx":
    interviews = pd.read_excel(data_file, sheet_name="Interviews")
    # Number of rounds
    int_round_df = interviews.groupby(['Round', 'Type of Interview', 'Location']).agg({
            'State': 'count',
            'Performance': 'mean',
            'Experience': 'mean'
        }).reset_index().sort_values("Round")
    just_round_df = interviews.groupby("Round").agg({
            'State': 'count',
            'Performance': 'mean',
            'Experience': 'mean'
        }).reset_index().sort_values("Round")
    # Type of role
    int_role_df = interviews.groupby(['Role Type', 'Type of Interview', 'Location']).agg({
            'State': 'count',
            'Round': 'mean',
            'Performance': 'mean',
            'Experience': 'mean'
        }).reset_index().sort_values("State", ascending=False)
    just_role_df = interviews.groupby('Role Type').agg({
            'State': 'count',
            'Round': 'mean',
            'Performance': 'mean',
            'Experience': 'mean'
        }).reset_index().sort_values("State", ascending=False)
    # Location
    int_loc_df = interviews.groupby('Location').agg({
            'State': 'count'
        }).reset_index().sort_values("State", ascending=False)
    # Type of interview
    int_type_df = interviews.groupby('Type of Interview').agg({
            'State': 'count'
        }).reset_index().sort_values("State", ascending=False)
    
    # CHARTS
    # Step 1: Convert to datetime
    st.subheader("Heatmap of interviews:")
    cal1, cal2, cal3 = st.columns([1,4,1])
    with cal2:
        interviews['Date'] = pd.to_datetime(interviews['Date'], format='%d-%b-%Y')

        # Step 2: Count occurrences per day
        daily_counts = interviews['Date'].value_counts().reset_index()
        daily_counts.columns = ['date', 'count']
        daily_counts = daily_counts.sort_values('date')

        # Step 3: Add calendar fields
        daily_counts['day'] = daily_counts['date'].dt.dayofweek     # 0 = Monday
        daily_counts['week'] = daily_counts['date'].dt.isocalendar().week
        daily_counts['month'] = daily_counts['date'].dt.strftime('%B')

        # Step 4: Plot calendar-style heatmap
        heatmap = alt.Chart(daily_counts).mark_rect().encode(
            x=alt.X('week:O', title='Week Number'),
            y=alt.Y('day:O', title='Day of Week',
                    sort=[0, 1, 2, 3, 4, 5, 6],
                    axis=alt.Axis(
                        labels=True,
                        labelExpr="['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][datum.value]"
                    )),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='blues'), title='Frequency'),
            tooltip=['date:T', 'count:Q']
        )
        st.altair_chart(heatmap, use_container_width=True)

    # Rounds 1
    st.subheader("Grouped by NUMBER OF ROUNDS:")
    color_field = st.selectbox(
            "Choose to color by:",
            options=["Type of Interview", "Location"]
        )
    r1, r2 = st.columns(2, border=True)
    with r1:
        round = alt.Chart(int_round_df).mark_bar().encode(
            x=alt.X("Round:O", title="Interview Round"),
            y=alt.Y("State:Q", title="Count"),
            color=alt.Color(f'{color_field}:N', title=color_field, scale=alt.Scale(scheme='blueorange')),
        )
        st.altair_chart(round, use_container_width=True)
    with r2:
        st.write("###")
        # Rounds line chart
        roundp = alt.Chart(just_round_df).mark_line(color='#206fb2').encode(
            x=alt.X("Round:O", title="Interview Round"),
            y=alt.Y("Performance:Q", title="Rating Performance & Experience")
        )
        rounde = alt.Chart(just_round_df).mark_line(color='#a8cee5').encode(
            x=alt.X("Round:O", title="Interview Round"),
            y=alt.Y("Experience:Q", title="")
        )
        layered_chart = alt.layer(roundp, rounde)
        st.altair_chart(layered_chart)  # or use layered_chart

    # Role
    st.subheader("Grouped by ROLE TYPE:")
    r1, r2 = st.columns(2, border=True)
    with r1:
        role = alt.Chart(int_role_df).mark_bar().encode(
            x=alt.X("Role Type:O", title="Role Type"),
            y=alt.Y("State:Q", title="Count"),
            color=alt.Color(f'{color_field}:N', title=color_field, scale=alt.Scale(scheme='blueorange')),
        )
        st.altair_chart(role, use_container_width=True)
    with r2:
        st.write("###")
        # Rounds line chart
        st.bar_chart(just_role_df, x="Role Type", y=['Experience', 'Performance'], stack=False)

else:
    st.text("Interviews not available with example data. Please ask to see the original data set.")

# ---------------------------------------- ROE
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Return on Effort")

# Scatterplot colored by application status
roe_formatted = roe.reset_index().rename(columns={"index": "Application Number"})
roe_formatted = roe_formatted.drop([21, 67])
# Get unique statuses from your data
unique_statuses = roe_formatted["Application Status"].unique().tolist()
# Drop the weird zero at the end
unique_statuses = unique_statuses[0:len(unique_statuses)-1]
# Streamlit multiselect widget
selected_statuses = st.multiselect(
    "Select application statuses to display:",
    options=unique_statuses,
    default=unique_statuses  # Show all by default
)
# Filter the data
filtered_data = roe_formatted[roe_formatted["Application Status"].isin(selected_statuses)]
# Scatterplot
scatter = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("Return on Effort:Q", title="Return on Effort"),
    color=alt.Color("Application Status:N", 
                    title="Status", 
                    scale=alt.Scale(domain=status_order, range=custom_colors)),
    tooltip=["Application Number", "Company Name", "Application Status", "Return on Effort"]
)
# Display
scatterplot = st.altair_chart(scatter, use_container_width=True)

more1, more2 = st.columns(2, border=True)

with more1:
    st.subheader("'Return on Effort' Definition")
    st.text("""This is a measure of "return on effort" or how much theoretical effort it should take for me to get the job. High values indicate that I should be an ideal applicant to the position. Low values indicate that it might be a stretch for me to get the job. Each point is measured by estimating the effort for each: platform, role type, and salary likelihood.""")
    st.text("Notes about the data:")
    st.html(
        "<ol style='padding-left: 5%'>" \
        "<li>Applications 21 and 67 are dropped in the scatterplot because they are extreme outliers in the master data.</li>" \
        "<li>Roles that have a '0' ROE did not have a salary listed on the job posting.</li>" \
        "<li>Referrals are not differentiated from cold applications in ROE - a better function might add a referral to the effort estimation.</li>" \
        "<li>More often than not, the ROE is negative in the master dataset. This means that I'm applying to jobs that I think are a stretch, which is good because I'm trying to be ambitious in this process. I'm applying to titles that aer unlikely with my experience (like product manager) and at salaries that are a relatively large increase.</li>" \
        "</ol>"
    )
    
with more2:
    # Status total
    st.text("Applications by status:")
    status = alt.Chart(status_df).mark_bar().encode(
        x=alt.X("Status:O", title="Status", sort=None),
        y=alt.Y("Applications In Status:Q", title="# In Status"),
        color=alt.Color("Status:N", 
                title="Status", 
                scale=alt.Scale(domain=status_order, range=custom_colors))
    )
    st.altair_chart(status, use_container_width=True)

    if data_file == "app_tracker.xlsx":

        # Estimated salary function
        st.text("Salary likelyhood function:")
        salaries = np.linspace(50, 200, 300)
        probs = likelihood(salaries)
        df = pd.DataFrame({'Salary': salaries, 'Likelihood': probs})
        line = alt.Chart(df).mark_line().encode(
            x=alt.X('Salary', title='Salary (k$)', axis=None),
            y=alt.Y('Likelihood', title='Likelihood', scale=alt.Scale(domain=[0,1]))
        )
        baseline_rule = alt.Chart(pd.DataFrame({'x':[avg_salary]})).mark_rule(color='red', strokeDash=[5,5]).encode(
            x='x'
        )
        text = alt.Chart(pd.DataFrame({'x':[115], 'y':[0.05]})).mark_text(
            align='left', baseline='middle', dx=5, color='red'
        ).encode(
            x='x',
            y='y',
        )
        chart = (line + baseline_rule + text)
        st.altair_chart(chart, use_container_width=True)
        st.text("The function above shows how salary impacts the ROE model. For all salaries below a certain point, I estimate I have a constant chance of getting those salaries based on my experience. After a certain value, the likelihood exponentially decreases to around 30%.")
        st.text("The red line is the average salary expectation.")

# ---------------------------------------- INSIGHTS

if data_file == "app_tracker.xlsx":
    st.write("#")
    st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
    c1, c2, c3 = st.columns([1, 6, 1])  # Adjust ratios to control padding

    with c2:
        st.header("Insights")
        st.text("Note: These points are based on my application journey and may not be true of different industries or levels of experience.")

    # Insights
    a, b, c, d, e = st.columns(5)
    with b:
        st.subheader("1")
        st.write("The most active hiring markets have been in marketing, AI, and data analytics.")
        st.subheader("4")
        st.write("Workday is a repetitve platform for applicants; account creation is time-consuming.")
    with c:
        st.subheader("2")
        st.write("There are 3-5 interviews in the average interview process. Generally: 1) recruiter call, 2) hiring manager interview, 3) case study, 4) final behavioral check.")
        st.subheader("5")
        st.write("Even companies with rigorous application processes send auto-denials; just because an application is harder to send does not make the job easier to obtain.")
    with d:
        st.subheader("3")
        st.write("Referrals have generally not been helpful.")
        st.subheader("6")
        st.write("I've tried resumes that are both 1 and 2 pages long. I've anecdotally noticed the most traction with 1 page.")
else:
    st.text("Insights not available with example data. Please ask to see the original data set.")