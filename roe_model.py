
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import os
import numpy as np
import openpyxl

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

# SHEETS
apps = pd.read_excel(data_file, sheet_name="Tracker")
roe = pd.read_excel(data_file, sheet_name="ROE Calculation")
interviews = pd.read_excel(data_file, sheet_name="Interviews")

# ---------------------------------------- CONSTANTS

# List of statuses
status_order = pd.unique(apps["Status"].dropna())
# Response Rate metrics
total_apps = apps[apps.columns[0]].count()
all_resp = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold', 'Denied', 'Offer']
real_resp = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold', 'Offer']
response_rate = sum(1 for app_stat in apps["Status"].dropna() if app_stat in all_resp)
real_response_rate = sum(1 for app_stat in apps["Status"].dropna() if app_stat in real_resp)
response_average = apps['Response Time (Days)'].dropna().mean()
response_max = apps['Response Time (Days)'].dropna().max()
response_max_company = apps.iloc[int(apps['Response Time (Days)'].dropna().idxmax()), 0]
# Interview metrics
num_interviews = sum(1 for app_stat in apps["Status"].dropna() if app_stat in real_resp)
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
        'Number of Interviews': 'sum'
    }).rename(columns={
        'Role Type': 'Applications In Status'
    }).reset_index().sort_values("Applications In Status", ascending=False)

# ---------------------------------------- HEADER

st.title("Job Application - Data Visualization")

# Layer 1 Columns
st.header("Graham Harris")
st.text("Since I was laid off in April 2025, I've been hard at work applying to new roles. This project is a capstone presentation of all of the data I've collected showcasing my data visualization skills.")
st.text("Example data is loaded on the public application - please ask for the master data set to see my actual application journey.")

# ---------------------------------------- CONTENTS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Table of Contents")
st.html(
    "<ol style='padding-left: 5%;'>"
        "<li><a href='#data-summary'>Data Summary</a></li>"
        "<li><a href='#application-breakdown'>Application Breakdown</a></li>"
        "<li><a href='#interviews'>Interviews</a></li>"
        "<li><a href='#return-on-effort'>Return on Effort</a></li>"
    "</ol>"
)
st.text("For more information, my resume, or to see the real data set, please email me at grahamh1019@gmail.com.")
st.text("Looking forward to hearing from you!")

# ---------------------------------------- DATA AGG
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Data Summary")

# Dataframes
col1, col2 = st.columns(2)
with col1:
    st.text("Applications grouped by INDUSTRY:")
    # Display the DataFrame
    st.dataframe(industry_df, hide_index=True)
with col2:
    st.text("Applications grouped by ROLE TYPE:")
    # Display the DataFrame
    st.dataframe(role_df, hide_index=True)

# Response data
st.html("<hr>")
st.subheader("Responses")
matrix1, matrix2 = st.columns(2)
with matrix1:
    rate = str('{0:.4g}'.format((response_rate/total_apps)*100)) + "%"
    st.metric("Response Rate (including auto-denials):", rate)
    rate2 = str('{0:.4g}'.format((real_response_rate/total_apps)*100)) + "%"
    st.metric("'Real' Response Rate (*excluding* auto-denials):", rate2)
    resp_avg_format = str('{0:.3g} days'.format(response_average))
    st.metric("Average time to respond (including auto-denials):", resp_avg_format)
    st.metric("Longest time to respond:", '{0:.3g}'.format(response_max) + " days (" + response_max_company + ")")
with matrix2:
    traction_rate = str('{0:.3g}'.format((current_interviews/last_four_weeks)*100)) + "%"
    st.metric("% of total applications currently in the interview phase:", traction_rate)  
st.html("<hr>")

# Company data
st.subheader("Companies")
matrix3, matrix4 = st.columns(2)
with matrix3:
    st.metric("Total number of applications:", total_apps)
with matrix4:
    st.metric("Number of UNIQUE companies:", unique_companies)

# ---------------------------------------- APP DATA
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Application Breakdown")

next1, next2 = st.columns(2, border=True)

with next1:
    st.subheader("Applications per WEEK:")
    # Create the chart
    weekly = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("Week:O", title="Week Number"),
        y=alt.Y("Applications Per Week:Q", title="Applications"),
        color=alt.value("#db9abc")
    )
    st.altair_chart(weekly, use_container_width=True)
    st.html("<hr>")

    st.subheader("Applications by ROLE:")
    # Create the chart
    platform = alt.Chart(role_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type", sort=None),
        y=alt.Y("Number of Applications:Q", title="# Applied To"),
        color=alt.value("#98A4EB")
    )
    st.altair_chart(platform, use_container_width=True)

with next2:
    st.subheader("Applications by PLATFORM:")
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Platform:O", title="Platform", sort=None),
        y=alt.Y("Applications Per Platform:Q", title="# Applications Sent"),
        color=alt.value("#d59287")
    )
    st.altair_chart(platform, use_container_width=True)
    st.html("<hr>")

    st.subheader("Interviews by WEEK APPLIED:")
    chart = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X('Week:O', title='Week Number'),
        y=alt.Y('Number of Interviews:Q', title='Total Interviews'),
        tooltip=['Week', 'Number of Interviews'],
        color=alt.value("#5c7579")
    )
    st.altair_chart(chart, use_container_width=True)
    st.text("Note: This chart shows the number of interviews per week based on when the application was sent, not when the actual interview occured.")

# ---------------------------------------- INTERVIEWS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Interviews")

# Prelim data data
st.subheader("By the numbers:")
matrix5, matrix6 = st.columns(2)
with matrix5:
    st.metric("Number of roles interviewed for:", num_interviews)
    st.metric("Average number of interviews per role:", apps['Number of Interviews'].dropna().mean())
    st.metric("Median number of interviews per role:", apps['Number of Interviews'].dropna().median())
with matrix6:
    st.metric("Total interviews:", int(sum_interviews))
    interview_max = apps['Number of Interviews'].dropna().max()
    interview_max_company = apps.iloc[int(apps['Number of Interviews'].dropna().idxmax()), 0]
    st.metric("Longest interview process:", '{0:.2g}'.format(interview_max) + " interviews (" + interview_max_company + ")")
st.html("<hr>")

# Drop NA just in case
st.subheader("Histogram of application response time:")
df_clean = apps.dropna(subset=['Response Time (Days)'])
# Optional filtering
min_day = int(df_clean['Response Time (Days)'].min())
max_day = int(df_clean['Response Time (Days)'].max())
bin_size = st.slider("Select x-axis scaling (in days)", 1, 10, 3)
# Histogram chart
hist = alt.Chart(df_clean).mark_bar().encode(
    alt.X("Response Time (Days):Q", bin=alt.Bin(step=bin_size), title="Response Time (Days)"),
    y=alt.Y("count():Q", title="Number of Applications"),
    tooltip=['count()']
).interactive()
st.altair_chart(hist)

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
    
# Interview heatmap
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
st.html("<hr>")

# Selectbox for interview stats
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

# ---------------------------------------- ROE
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Return on Effort")

# Scatterplot colored by application status
roe_formatted = roe.reset_index().rename(columns={"index": "Application Number"})
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
st.subheader('Chance of Success')
scatter = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("Chance of Success:Q", title="Chance of Success"),
    color=alt.Color("Application Status:N", 
                    title="Status",
                    scale=alt.Scale(scheme='turbo')),
    tooltip=["Application Number", "Company Name", "Application Status", "Chance of Success"]
)
# Display
scatterplot = st.altair_chart(scatter, use_container_width=True)

more1, more2 = st.columns(2, border=True)
with more1:
    st.markdown("""
            **'Chance of Success' Definition**: 
            This is a measure of the likelihood of success, or the chance I think I have of getting an offer. High values indicate that I should be an ideal applicant to the position. Low values indicate that it might be a stretch for me to get the job. Each point is measured by estimating the effort for each: role, average salary, salary range (max - min salary), and industry.""")
    st.text("Notes about the data:")
    st.html(
        "<ol style='padding-left: 5%'>" \
        "<li>Roles that have an exact '0.5' chance of success did not have a salary listed on the job posting.</li>" \
        "<li>The salary range is a confidence score. When companies have narrow salary ranges (IE 80-90k has a 10k range) the company likely has a set expectation for the role. If the range is extremely high (IE $100k or more) then the role seems ambiguous and it's not clear how the company is hiring or what a realistic salary is, and they may even be hiring for multiple levels of experience.</li>" \
        "</ol>"
    )

    total_above_1 = (roe['Chance of Success'] > 0.5).sum()
    responses_above_1 = ((roe['Chance of Success'] > 0.5) & 
                         (roe['Application Status'].isin(['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold']))).sum()
    positive_chance = (responses_above_1/total_above_1)*100
    total_accuracy = real_response_rate/total_apps
    accuracy = (positive_chance-total_accuracy)/total_accuracy-100
    st.metric("Real response rate (exluding auto-denials):", 
              rate2)
    st.metric("Response rate where the chance of success is above 50%:", 
              f"{positive_chance:.2f}%")
    st.metric("Accuracy of the chance of success metric:", 
              f"{accuracy:.2f}%")
    st.text("This means that applications with more than a 50% chance of success have a " + f"{(accuracy):.2f}%" + " higher chance of leading to a response than applications below 50% chance.")
with more2:
    # Status total
    st.text("Applications by status:")
    status = alt.Chart(status_df).mark_bar().encode(
        x=alt.X("Status:O", title="Status", sort=None),
        y=alt.Y("Applications In Status:Q", title="# In Status"),
        color=alt.Color("Status:N", 
                title="Status",
                scale=alt.Scale(scheme='turbo'))
    )
    st.altair_chart(status, use_container_width=True)

# Scatterplot
st.subheader('Application Effort')
effort_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("Application Effort:Q", title="Application Effort"),
    color=alt.Color("Application Status:N", 
                    title="Status",
                    scale=alt.Scale(scheme='turbo')),
    tooltip=["Application Number", "Company Name", "Application Status", "Application Effort"]
)
# Display
effort_scatterplot = st.altair_chart(effort_plot, use_container_width=True)
st.markdown("""
        **'Effort' Definition**: 
        This is a measure of how much effort has been put into an application. High values indicate that a lot of effort has been put into an application and low values indicate low levels of effort was put in.  Each point is measured by estimating the effort for each: status (applied, interviewing, rejected, etc), platform, and number of interviews.""")
st.text("Notes about the data:")
st.html(
        "<ol style='padding-left: 5%'>" \
        "<li>Each interview linearly increases the effort.</li>" \
        "<li>Platforms with 'easy apply' are rated more 'easy' than platforms that need fresh information with each application.</li>" \
        "</ol>"
)

# Scatterplot
st.subheader('Return on Effort')
roe_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("ROE:Q", title="Return on Effort"),
    color=alt.Color("Application Status:N", 
                    title="Status",
                    scale=alt.Scale(scheme='turbo')),
    tooltip=["Application Number", "Company Name", "Application Status", "ROE"]
)
# Display
roe_scatterplot = st.altair_chart(roe_plot, use_container_width=True)
st.markdown("""
        **'Return on Effort' Definition**: 
        The return on investment, or in this case, return on effort (ROE). For example, if the ROE is 3, there would be a 3X return on the effort that I put into the application. Return on effort is qualitative and doesn't exactly capture the experience of an application. For example, getting an interview from an application does more than just reward effort - it signifies that something was right in the application (like resume, cover letter, experience, etc.) and validates the direction of future applications. In the end, the only thing that really matters is getting an offer, so offers are weighted at a 10X value.""")

st.write("#")
st.html("<a href='#job-application-data-visualization'>Return to Top</a>")