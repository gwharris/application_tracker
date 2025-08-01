
import pandas as pd
import streamlit as st
import altair as alt
import os
import openpyxl
from  streamlit_vertical_slider import vertical_slider 
import streamlit_toggle

# Wide mode
st.set_page_config(layout="wide", page_title="Application Data")

# ---------------------------------------- READ FILE
# Check if file exists. Throws error if file is not present

# File names
DEFAULT_FILE = "example_app_tracker.xlsx"
REAL_FILE = "app_tracker.xlsx"

# User upload
uploaded_file = st.file_uploader("Upload your own application tracker here:", type=["xlsx", "xls"])

# Load data
if uploaded_file is not None:
    apps = pd.read_excel(uploaded_file, sheet_name="Tracker")
    roe = pd.read_excel(uploaded_file, sheet_name="ROE Calculation")
    interviews = pd.read_excel(uploaded_file, sheet_name="Interviews")
    st.success("✅ Uploaded file.")
elif os.path.exists(REAL_FILE):
    apps = pd.read_excel(REAL_FILE, sheet_name="Tracker")
    roe = pd.read_excel(REAL_FILE, sheet_name="ROE Calculation")
    interviews = pd.read_excel(REAL_FILE, sheet_name="Interviews")
    st.info("ℹ️ Running app locally with app_tracker.xlsx.")
else:
    apps = pd.read_excel(DEFAULT_FILE, sheet_name="Tracker")
    roe = pd.read_excel(DEFAULT_FILE, sheet_name="ROE Calculation")
    interviews = pd.read_excel(DEFAULT_FILE, sheet_name="Interviews")
    st.warning("⚠️ Master data set not found. Using default example data.")

# ---------------------------------------- CONSTANTS

# These constants are used for error handling
apps_columns = list(apps.columns)
roe_columns = list(roe.columns)
interview_columns = list(interviews.columns)

# Number of apps
total_apps = apps[apps.columns[0]].dropna().count()

# List of ALL statuses
status_order = pd.unique(apps["Status"].dropna())
# Lists of Positive response stats
all_resp = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 
            'On Hold', 'Denied', 'Viewed', 'Offer', 'No Offer'] # Denied and Viewed are auto responses
real_resp = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold', 'Offer', 'No Offer'] # So real != Denied, Viewed

# Apps DF where Pending is dropped
apps_nopend = apps[apps["Status"].str.contains("Pending")==False]
total_nopend_apps = apps_nopend[apps_nopend.columns[0]].dropna().count()

unique_companies = len(pd.unique(apps['Company']))
avg_int_per_role = apps['Number of Interviews'].dropna().mean()

# Response rate calcs
response_number = sum(1 for app_stat in apps_nopend["Status"].dropna() if app_stat in all_resp)
real_response_number = sum(1 for app_stat in apps_nopend["Status"].dropna() if app_stat in real_resp)

# Response time (agnostic of Pending since response time means they had to respond)
response_average = apps['Response Time (Days)'].dropna().mean()
real_response_average = apps[apps['Status'].isin(real_resp)]['Response Time (Days)'].dropna().mean()
longest_response = apps['Response Time (Days)'].dropna().max()
longest_response_company = apps.iloc[int(apps['Response Time (Days)'].dropna().idxmax()), 0]
num_weeks = apps["Week"].max() # Number of weeks for later calc

# Interview metrics
num_interviewed_at = sum(1 for app_stat in apps["Status"].dropna() if app_stat in real_resp)
currently_interviewing = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing"])
sum_interviews = interviews[interviews.columns[0]].dropna().count() # NOT sum of apps interview column cause duplicates

interview_max = apps['Number of Interviews'].dropna().max()
interview_max_company = apps.iloc[int(apps['Number of Interviews'].dropna().idxmax()), 0]

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

# Used in group by dataframes
def count_status(status_list):
    return lambda x: x.isin(status_list).sum()

# Returns a df in teh right formatting for apps
def groupby_percents(sheet, col_name):
    rdf = sheet.groupby(col_name).agg(
        Applications=('Status', 'count'),
        Companies=('Company', pd.Series.nunique),
        Interviews=('Number of Interviews', 'sum'),
        Salary_Min=('Salary Min (Thousands)', 'mean'),
        Salary_Max=('Salary Max (Thousands)', 'mean'),
        All_Positive=('Status', count_status(all_resp)),
        Real_Positive=('Status', count_status(real_resp)),
        Response_Time=('Response Time (Days)', 'mean')
    ).reset_index().sort_values("Applications", ascending=False)
    # Create response % columns
    rdf['Total Responses'] = rdf['All_Positive'] / rdf['Applications'] * 100
    rdf['Total Responses'] = rdf['Total Responses'].apply('{:.1f}%'.format)
    rdf['Real Responses'] = rdf['Real_Positive'] / rdf['Applications'] * 100
    rdf['Real Responses'] = rdf['Real Responses'].apply('{:.1f}%'.format)
    rdf['Salary_Min'] = rdf['Salary_Min'].apply('${:.2f}'.format)
    rdf['Salary_Max'] = rdf['Salary_Max'].apply('${:.2f}'.format)
    rdf['Response_Time'] = rdf['Response_Time'].apply('{:.2f}'.format)
    # Drop extra columns
    rdf = rdf.drop('All_Positive', axis=1)
    rdf = rdf.drop('Real_Positive', axis=1)
    rdf = rdf.rename(columns={
        'Applications': '# of Applications',
        'Companies': '# of Companies',
        'Salary_Min': 'Avg Min K',
        'Salary_Max': 'Avg Max K',
        'Response_Time': 'Avg DTR'
    })
    return rdf

# For DFs that need less groupby fields
def groupby_smaller(sheet, count, col_name, rename, sort):
    rdf = sheet.groupby(col_name).agg({
        count: 'count',
        'Number of Interviews': 'sum',
        'Response Time (Days)': 'mean'
    }).rename(columns={
        count: rename
    }).reset_index().sort_values(sort, ascending=False)
    return rdf

# ---------------------------------------- GROUP BYS
# Dataframes from the Applications page that are grouped by category

industry_df = groupby_percents(apps, "Industry")
role_df = groupby_percents(apps, "Role Type")
comp_size_df = groupby_percents(apps, "Company Size")
comp_size_df = comp_size_df.drop(["Avg Min K", "Avg Max K"], axis=1)

weekly_df = groupby_smaller(apps, "Status", "Week", "Applications Per Week", "Week")
weekly_df = weekly_df.drop(0) # Drop the -14 values
last_four_weeks = weekly_df['Applications Per Week'].head(4).sum()

platform_df = groupby_smaller(apps, "Status", "Platform", "Applications Per Platform", "Applications Per Platform")
status_df = groupby_smaller(apps, "Role Type", "Status", "Applications In Status", "Applications In Status")

cover_df = groupby_percents(apps, "Cover Letter")
cover_df = cover_df.sort_values("# of Applications", ascending=False)
cover_df = cover_df.drop(["Avg Min K", "Avg Max K"], axis=1)

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
    }).rename(columns={
        'State': "Number of Interviews"
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

# ---------------------------------------- HEADER

st.title("Job Application - Data Visualization")

# Layer 1 Columns
st.header("Graham Harris")
st.text("Since I was laid off in April 2025, I've been hard at work applying to new roles. This project is a capstone presentation of all of the data I've collected showcasing my data visualization skills.")
st.text("Example data is loaded on the public application - please ask for the master data set to see my actual application journey.")
st.text("Choose the colors for the graphs:")
c1, c2, c3, c4 = st.columns(4)
with c1:
    color1 = st.color_picker("Color 1", "#26bce1")
with c2:
    color2 = st.color_picker("Color 2:", "#4a58dd")
# CHART COLORS
gradient = [color1, color2]
barcolor = "turbo"

# ---------------------------------------- CONTENTS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Table of Contents")
st.html("<ol style='padding-left: 5%;'>"
        "<li><a href='#data-summary'>Data Summary</a></li>"
        "<li><a href='#application-breakdown'>Application Breakdown</a></li>"
        "<li><a href='#interviews'>Interviews</a></li>"
        "<li><a href='#return-on-effort'>Return on Effort</a></li>"
    "</ol>")
st.text("For more information, my resume, or to see the real data set, please email me at grahamh1019@gmail.com.")
st.text("Looking forward to hearing from you!")

# ---------------------------------------- DATA AGG
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Data Summary")

st.subheader("Applications")
st.metric("Total number of applications:", total_apps)
# Dataframes
col1, col2 = st.columns(2, gap='large')
with col1:
    st.text("Applications grouped by INDUSTRY:")
    st.dataframe(industry_df, hide_index=True)
    st.text("'DTR' stands for 'Days to Respond' and measures how long it takes companies to send a response to an application.")
    st.text("'Real' responses are responses that are not automated denials. The statuses that are not considered 'real' are 'Denied' and 'Viewed'. 'Denied' indicates an automated denial message and 'Viewed' means that a notification was received that the company opened the application, but did not respond.")
with col2:
    st.text("Applications grouped by ROLE TYPE:")
    st.dataframe(role_df, hide_index=True)

col3, col4 = st.columns(2, gap='large')
with col3:
    # Create the chart
    platform = alt.Chart(industry_df).mark_bar().encode(
        x=alt.X("Industry:O", title="Industry", sort=None),
        y=alt.Y("# of Applications:Q", title="# Applications Sent"),
        color=alt.value(color1)
    )
    st.altair_chart(platform, use_container_width=True)
    st.text("In the master data, the industry 'Recruiter' represents listings posted by a recruiting agency on behalf of another company. The overwhelming majority of postings like these are from financial/investment banking firms. The response rate for these kinds of listings is abysmal.")
with col4:
    # Create the chart
    platform = alt.Chart(role_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type", sort=None),
        y=alt.Y("# of Applications:Q", title="# Applied To"),
        color=alt.value(color2)
    )
    st.altair_chart(platform, use_container_width=True)

st.html("<hr>")
# Company data
st.subheader("Companies")
companies1, companies2 = st.columns(2)
with companies1:
    st.text("Applications by COMPANY SIZE:")
    st.dataframe(comp_size_df, hide_index=True)
with companies2:
    st.metric("Number of UNIQUE companies:", unique_companies)

# Response data
st.html("<hr>")
st.subheader("Responses")
st.text("'Pending' applications are not considered in response metrics to keep data historical and not current.")
matrix1, matrix2 = st.columns(2)
with matrix1:
    all_response_rate = str('{0:.4g}'.format((response_number/total_apps)*100)) + "%"
    st.metric("Total Response Rate (including auto-denials):", all_response_rate)
    real_response_rate = str('{0:.4g}'.format((real_response_number/total_apps)*100)) + "%"
    st.metric("Total 'Real' Response Rate (*excluding* auto-denials):", real_response_rate)
    resp_avg_format = str('{0:.3g} days'.format(response_average))
    st.metric("Average time to respond (including auto-denials):", resp_avg_format)
    real_resp_avg_format = str('{0:.3g} days'.format(real_response_average))
    st.metric("Real average time to respond (*excluding* auto-denials):", real_resp_avg_format)
with matrix2:
    traction_rate = str('{0:.3g}'.format((currently_interviewing/last_four_weeks)*100)) + "%"
    st.metric("% of applications in the past 4 weeks currently in the interview phase:", traction_rate)  
    st.metric("Longest time to respond:", '{0:.3g}'.format(longest_response) + " days (" + longest_response_company + ")")

# ---------------------------------------- APP DATA
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Application Breakdown")
st.text("Details about the actual applications themselves.")

next1, next2 = st.columns(2, border=True, gap="medium")
with next1:
    st.subheader("Applications per WEEK:")
    # Create the chart
    weekly = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("Week:O", title="Week Number"),
        y=alt.Y("Applications Per Week:Q", title="Applications"),
        color=alt.value(color1)
    )
    st.altair_chart(weekly, use_container_width=True)
    st.text("Average applications per week: " + '{0:.3g}'.format(total_apps/num_weeks))
with next2:
    st.subheader("Applications by PLATFORM:")
    # Create the chart
    platform = alt.Chart(platform_df).mark_bar().encode(
        x=alt.X("Platform:O", title="Platform", sort=None),
        y=alt.Y("Applications Per Platform:Q", title="# Applications Sent"),
        color=alt.value(color2)
    )
    st.altair_chart(platform, use_container_width=True)

# Histogram of response time
st.html("<hr>")
st.subheader("Application Response Time:")
st.text("How long does it take a company to respond to my application?")
df_clean = apps.dropna(subset=['Response Time (Days)'])
# Optional filtering
min_day = int(df_clean['Response Time (Days)'].min())
max_day = int(df_clean['Response Time (Days)'].max())

hist1, hist2 = st.columns([7,1])
# Scale to measure application
with hist2:
    bin_size = vertical_slider(
        label = "X Scaling:",  #Optional
        key = "vert_01" ,
        # height = 300, #Optional - Defaults to 300
        thumb_shape = "square", #Optional - Defaults to "circle"
        step = 1, #Optional - Defaults to 1
        default_value=3 ,#Optional - Defaults to 0
        min_value= 1, # Defaults to 0
        max_value= 10, # Defaults to 10
        track_color = color2, #Optional - Defaults to Streamlit Red
        slider_color = color1, #Optional
        thumb_color= color1, #Optional - Defaults to Streamlit Red
        value_always_visible = True , #Optional - Defaults to False
    )
with hist1:
    # Histogram chart
    hist = alt.Chart(df_clean).mark_bar().encode(
        alt.X("Response Time (Days):Q", bin=alt.Bin(step=bin_size), title="Response Time (Days)"),
        y=alt.Y("count():Q", title="Number of Applications"),
        tooltip=['count()'],
        color=alt.value(color1)
    ).interactive()
    st.altair_chart(hist)

# Cover Letter info
st.html("<hr>")
st.subheader("Cover Letter Details")
st.text("How successful are cover letters?")
cov1, cov2 = st.columns(2, gap="medium", border=True)
with cov1:
    st.dataframe(cover_df, hide_index=True)
with cov2:
    st.markdown("""
        Notes:

        Cover letter metrics were not tracked until 7/28 in the master data.
        
    """)
    st.html(
        "Status Breakdown:"
        "<ul style='padding-left: 5%'>" \
        "<li>Yes = Cover letter was sent.</li>" \
        "<li>No = Cover letter was not sent.</li>" \
        "<li>Unavailable = There was no place to add a cover letter on the application.</li>" \
        "<li>Questionnaire = In leiu of a cover letter, there were short-answer response questions.</li>" \
        "</ul>"
    )

# ---------------------------------------- INTERVIEWS
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
st.header("Interviews")

# Interview charts
st.subheader("By the numbers:")
matrix5, matrix6 = st.columns(2, border=True, gap="medium")
with matrix5:
    st.subheader("Interviews by WEEK APPLIED:")
    chart = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X('Week:O', title='Week Number'),
        y=alt.Y('Number of Interviews:Q', title='Total Interviews'),
        tooltip=['Week', 'Number of Interviews'],
        color=alt.value(color1)
    )
    st.altair_chart(chart, use_container_width=True)
    st.text("Note: This chart shows the number of interviews per week based on when the application was sent, not when the actual interview occured. This helps show how successful a resume is on any given week and how changes to a resume impact interviews.")
    st.text("There's usually a 2-3 week lag time in getting interviews due to response time turnaround.")   
with matrix6:
    st.subheader("Number of interviews, by round:")
    round_chart = alt.Chart(just_round_df).mark_bar().encode(
        x=alt.X('Round:O', title='Round'),
        y=alt.Y('Number of Interviews:Q', title='Total Interviews'),
        tooltip=['Round', 'Number of Interviews'],
        color=alt.value(color2)
    )
    st.altair_chart(round_chart, use_container_width=True)
    st.text("'Rounds' are defined by a separate, new, scheduled item. For example, going in-person to an interview for 3 back-to-back meetings is considered only one round, even if 3 meetings occured. If multiple interviews happen for the same round on different dates, they are considered the same round but separate interviews (ie: meeting with 3 people, but each interview is scheduled for a different day.)")

# Metrics
matrix7, matrix8 = st.columns(2, gap="medium")
with matrix7:
    st.metric("Number of roles interviewed for:", num_interviewed_at)
    st.metric("Average number of interviews per role:", '{0:.3g}'.format(avg_int_per_role))
    st.metric("Average number of interviews per week:", '{0:.3g}'.format(sum_interviews/num_weeks))
with matrix8: 
    st.metric("Total interviews:", int(sum_interviews))
    st.metric("Longest interview process:", '{0:.2g}'.format(interview_max) + " interviews (" + interview_max_company + ")")

st.html("<hr>")

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
            color=alt.Color('count:Q', scale=alt.Scale(range=gradient), title='Frequency'),
            tooltip=['date:T', 'count:Q']
        )
    st.altair_chart(heatmap, use_container_width=True)
st.html("<hr>")

# Selectbox for interview stats
st.subheader("Breakdown of Interviews")
color_field = st.selectbox(
    "Choose to color by:",
    options=["Type of Interview", "Location"]
    )
r1, r2 = st.columns(2, border=True, gap='medium')
with r1:
    st.subheader("Grouped by NUMBER OF ROUNDS:")
    round = alt.Chart(int_round_df).mark_bar().encode(
        x=alt.X("Round:O", title="Interview Round"),
        y=alt.Y("State:Q", title="Count"),
        color=alt.Color(f'{color_field}:N', title=color_field, scale=alt.Scale(scheme=barcolor)),
    )
    st.altair_chart(round, use_container_width=True)
with r2:
    st.subheader("Grouped by ROLE TYPE:")
    role = alt.Chart(int_role_df).mark_bar().encode(
        x=alt.X("Role Type:O", title="Role Type"),
        y=alt.Y("State:Q", title="Count"),
        color=alt.Color(f'{color_field}:N', title=color_field, scale=alt.Scale(scheme=barcolor)),
    )
    st.altair_chart(role, use_container_width=True)

st.subheader("Breakdown By (Perceived) Performance")
st.text("Performance measures how well I adapted to the interview and how successful I feel I was.")
st.text("Experience is how enjoyable the interview was/how well the interviewer executed the interview.")
st.text("Both are rated 1-5, where 5 is the most positive and 1 is the most negative.")
r1, r2 = st.columns(2)
with r1:
    # Rounds line chart
    roundp = alt.Chart(just_round_df).mark_line(color=color2).encode(
        x=alt.X("Round:O", title="Interview Round"),
        y=alt.Y("Performance:Q", title="Performance")
    )
    rounde = alt.Chart(just_round_df).mark_line(color=color1).encode(
        x=alt.X("Round:O", title="Interview Round"),
        y=alt.Y("Experience:Q", title="Experience")
    )
    layered_chart = alt.layer(rounde, roundp)
    st.altair_chart(layered_chart)  # or use layered_chart
with r2:
    # Rounds line chart
    melted = just_role_df.melt(
        id_vars='Role Type',
        value_vars=['Performance', 'Experience'],
        var_name='Metric',
        value_name='Value'
    )

    # Create grouped bar chart
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X('Role Type:N', title='Role Type'),
        xOffset=alt.XOffset('Metric:N'),  # This creates side-by-side bars
        y=alt.Y('Value:Q', title='Score'),
        color=alt.Color('Metric:N', title='Metric', scale=alt.Scale(range=[color1, color2])),
        tooltip=['Role Type', 'Metric', 'Value']
    ).properties(width=500)

    st.altair_chart(chart, use_container_width=True)

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
                    scale=alt.Scale(scheme=barcolor)),
    tooltip=["Application Number", "Company Name", "Application Status", "Chance of Success"]
)
# Display
scatterplot = st.altair_chart(scatter, use_container_width=True)

more1, more2 = st.columns(2, border=True, gap='medium')
with more1:
    st.markdown("""
            **'Chance of Success' Definition**: 
            This is a measure of the likelihood of success, or the chance I think I have of getting an offer. High values indicate that I should be an ideal applicant to the position. Low values indicate that it might be a stretch for me to get the job. Each point is measured by estimating the effort for each: role, average salary, salary range (max - min salary), and industry.""")
    st.text("Notes about the metric:")
    st.html(
        "<ol style='padding-left: 5%'>" \
            "<li>Roles that have an exact '0.5' chance of success did not have a salary listed on the job posting.</li>" \
            "<li>The salary range is a confidence score. When companies have narrow salary ranges (IE 80-90k has a 10k range) the company likely has a set expectation for the role. If the range is extremely high (IE $100k or more) then the role seems ambiguous and it's not clear how the company is hiring or what a realistic salary is, and they may even be hiring for multiple levels of experience.</li>" \
            "<li>In the master data set, most of the roles I apply to fall below 50% success. That's okay - I'm trying to be ambitious with the process and am applying to roles that are outside my comfort zone/experience.</li>" \
        "</ol>"
    )

    total_above_1 = (roe['Chance of Success'] > 0.5).sum()
    responses_above_1 = ((roe['Chance of Success'] > 0.5) & 
                         (roe['Application Status'].isin(['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold']))).sum()
    positive_chance = (responses_above_1/total_above_1)*100
    total_accuracy = real_response_number/total_apps
    accuracy = (positive_chance-total_accuracy)/total_accuracy-100
    st.metric("Real response rate (excluding auto-denials):", real_response_rate)
    st.metric("Response rate where the chance of success is above 50%:", 
              f"{positive_chance:.2f}%")
    st.metric("Accuracy of the chance of success metric:", 
              f"{accuracy:.2f}%")
    st.text("This means that applications with more than a 50% chance of success are " + f"{(accuracy * 2/100):.2f}X" + " more likely to result in a response than applications below 50% chance.")
with more2:
    # Status total
    st.text("Applications by status:")
    status = alt.Chart(status_df).mark_bar().encode(
        x=alt.X("Status:O", title="Status", sort=None),
        y=alt.Y("Applications In Status:Q", title="# In Status"),
        color=alt.Color("Status:N", 
                title="Status",
                scale=alt.Scale(scheme=barcolor))
    )
    st.altair_chart(status, use_container_width=True)
    st.text("Notes about application status:")
    st.html(
        "<ol style='padding-left: 5%'>" \
            "<li>The 'Viewed' status in the master data is exclusive to LinkedIn applications. LinkedIn sends an email notification when companies view or download resumes. If the company does not respond, the application is left in the 'Viewed' status.</li>" \
            "<li>The 'Bailed' status means that I decided to no longer pursue the application for a number of reasons, including: feeling like I was being scammed, the interviewers did not impress me, or the role sounded like a bad fit after learning more information.</li>" \
        "</ol>"
    )

# Scatterplot
st.html("<hr>")
st.subheader('Application Effort')
effort_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("Application Effort:Q", title="Application Effort"),
    color=alt.Color("Application Status:N", 
                    title="Status",
                    scale=alt.Scale(scheme=barcolor)),
    tooltip=["Application Number", "Company Name", "Application Status", "Application Effort"]
)
# Display
effort_scatterplot = st.altair_chart(effort_plot, use_container_width=True)
st.markdown("""
        **'Effort' Definition**: 
        This is a measure of how much effort has been put into an application. High values indicate that a lot of effort has been put into an application and low values indicate low levels of effort was put in.  Each point is measured by estimating the effort for each: platform and number of interviews.""")
st.text("Notes about the data:")
st.html(
        "<ol style='padding-left: 5%'>" \
        "<li>Each interview linearly increases the effort.</li>" \
        "<li>Platforms with 'easy apply' are rated more 'easy' than platforms that need fresh information with each application.</li>" \
        "</ol>"
)

# Scatterplot
st.html("<hr>")
st.subheader('Return on Effort')
roe_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X("Application Number:Q", title="Application Number"),
    y=alt.Y("ROE:Q", title="Return on Effort"),
    color=alt.Color("Application Status:N", 
                    title="Status",
                    scale=alt.Scale(scheme=barcolor)),
    tooltip=["Application Number", "Company Name", "Application Status", "ROE"]
)
# Display
roe_scatterplot = st.altair_chart(roe_plot, use_container_width=True)
st.markdown("""
        **'Return on Effort' Definition**: 
        The return on investment, or in this case, return on effort (ROE). For example, if the ROE is 3, there would be a 3X return on the effort that I put into the application. Return on effort is qualitative and doesn't exactly capture the experience of an application. For example, getting an interview from an application does more than just reward effort - it signifies that something was right in the application (like resume, cover letter, experience, etc.) and validates the direction of future applications.""")

st.write("#")
st.html("<a href='#job-application-data-visualization'>Return to Top</a>")