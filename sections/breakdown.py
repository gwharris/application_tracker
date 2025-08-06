import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
import altair as alt

# Homebrew files
import sections.constants as constants
from sections.methods import *

# Color constants
color1 = constants.COLOR1
color2 = constants.COLOR2

def show(apps):
    st.title("Application Data")
    try:
        # ----------------------------------------------- Constants
        # Number of apps
        total_apps = apps[apps.columns[0]].dropna().count()

        # Apps DF where Pending is dropped
        apps_nopend = apps[apps["Status"].str.contains("Pending")==False]

        unique_companies = len(pd.unique(apps['Company']))

        # Response rate calcs
        response_number = sum(1 for app_stat in apps_nopend["Status"].dropna() if app_stat in constants.ALL_RESP)
        real_response_number = sum(1 for app_stat in apps_nopend["Status"].dropna() if app_stat in constants.REAL_RESP)

        # Response time (only historical, not considering Pending)
        response_average = apps['Response Time (Days)'].dropna().mean()
        real_response_average = apps[apps['Status'].isin(constants.REAL_RESP)]['Response Time (Days)'].dropna().mean()
        longest_response = apps['Response Time (Days)'].dropna().max()
        longest_response_company = apps.iloc[int(apps['Response Time (Days)'].dropna().idxmax()), 0]
        num_weeks = apps["Week"].max() # Number of weeks for later calc

        # Interview metrics
        currently_interviewing = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing"])

        # ----------------------------------------------- Dataframes
        industry_df = groupby_percents(apps, "Industry")
        role_df = groupby_percents(apps, "Role Type")
        comp_size_df = groupby_percents(apps, "Company Size")
        comp_size_df = comp_size_df.drop(["Avg Min K", "Avg Max K"], axis=1)
        platform_df = groupby_percents(apps, "Platform")

        weekly_df = groupby_percents(apps, "Week")
        if weekly_df.iloc[len(weekly_df)-1][0] < 0: # Drop extra auto values if they exist
            weekly_df = weekly_df.drop(0) 
        last_four_weeks = weekly_df['# of Applications'].head(4).sum()

        resume_df = groupby_percents(apps, "Resume ID")
        resume_df = resume_df.sort_values("# of Applications", ascending=False)
        resume_df = resume_df.drop(["Avg Min K", "Avg Max K"], axis=1)

        cover_df = groupby_percents(apps, "Cover Letter")
        cover_df = cover_df.sort_values("# of Applications", ascending=False)
        cover_df = cover_df.drop(["Avg Min K", "Avg Max K"], axis=1)

        month_df = groupby_percents(apps, "Month").sort_values("Month")
        month_df = month_df.drop(["Avg Min K", "Avg Max K"], axis=1)

        # ----------------------------------------------- Calculations
        st.header("Job Details")
        st.write("Data about the job posting, like industry, title, company, etc.")
        # Dataframes
        col1, col2 = st.columns(2, border=True, gap='large')
        with col1:
            st.text("Applications grouped by INDUSTRY:")
            st.dataframe(industry_df, hide_index=True)
            st.text("'DTR' stands for 'Days to Respond' and measures how long it takes companies to send a response to an application.")
            st.text("More details about responses are available in the Glossary.")
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
        companies1, companies2 = st.columns(2, gap='medium')
        with companies1:
            st.text("Applications by COMPANY SIZE:")
            st.dataframe(comp_size_df, hide_index=True)
            st.text("Note: 'DTR' stands for 'Days to Respond'.")
        with companies2:
            st.metric("Total number of applications:", total_apps)
            st.metric("Number of unique companies:", unique_companies)
            st.metric("Average number of applications per company:", '{:.2f}'.format(total_apps/unique_companies))

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

        # Histogram of response time
        st.subheader("Application Response Time:")
        st.text("How long does it take a company to respond to my application?")
        hist_apps_clean = apps.dropna(subset=['Response Time (Days)'])
        # Optional filtering
        min_day = int(hist_apps_clean['Response Time (Days)'].min())
        max_day = int(hist_apps_clean['Response Time (Days)'].max())

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
            hist = alt.Chart(hist_apps_clean).mark_bar().encode(
                alt.X("Response Time (Days):Q", bin=alt.Bin(step=bin_size), title="Response Time (Days)"),
                y=alt.Y("count():Q", title="Number of Applications"),
                tooltip=['count()'],
                color=alt.value(color1)
            ).interactive()
            # Text layer with aggregate count
            hist_text = hist.mark_text(
                align='center',
                baseline='bottom',
                dy=-2
            ).encode(
                text='count():Q'
            )
            st.altair_chart(hist)

            # ----------------------------------------------- More Calculations
            st.write("#")
            st.html("<hr style='border: 5px solid black; border-radius: 5px'>")
            st.header("Application Data")
            st.text("Details about the actual applications themselves, like cover letter metrics, resume differences, etc.")

            next1, next2 = st.columns(2, border=True, gap="medium")
            with next1:
                st.subheader("Applications per WEEK:")
                # Create the chart
                weekly = alt.Chart(weekly_df).mark_bar().encode(
                    x=alt.X("Week:O", title="Week Number"),
                    y=alt.Y("# of Applications:Q", title="Applications"),
                    color=alt.value(color1)
                )
                # Text labels showing response_rate
                weekly =  weekly + bar_text(weekly, -16, "Total Responses") + bar_text(weekly, -4, "Real Responses")
                # Chart
                st.altair_chart(weekly, use_container_width=True)
                st.text("Average applications per week: " + '{0:.3g}'.format(total_apps/num_weeks))
            with next2:
                st.subheader("Applications by PLATFORM:")
                # Create the chart
                platform = alt.Chart(platform_df).mark_bar().encode(
                    x=alt.X("Platform:O", title="Platform", sort=None),
                    y=alt.Y("# of Applications:Q", title="# Applications Sent"),
                    color=alt.value(color2)
                )
                # Text labels showing response_rate
                platform =  platform + bar_text(platform, -16, "Total Responses") + bar_text(platform, -4, "Real Responses")
                # Chart
                st.altair_chart(platform, use_container_width=True)
            st.text("Key: 'T' is Total Response rate, 'R' is Real Response rate.")
            st.text("Ex: In Week 1, the total response rate was T and the real response rate was R.")

            st.html("<hr>")
            st.subheader("Month by Month")
            mon1, mon2 = st.columns(2, gap='medium')
            with mon1:
                try:
                    month_df = month_df[month_df["# of Applications"] != 0]
                except:
                    st.text("Error dropping null value months.")
                st.dataframe(month_df, hide_index=True)
                st.text("Note: 'DTR' stands for 'Days to Respond'.")
            with mon2:
                st.text("How has my process changed over time?")
                st.text("Usually there's a 2-3 week lag in responses from companies, so data becomes more accurate as revisions come in.")

            # Cover Letter info
            st.html("<hr>")
            st.subheader("Resume Details")
            st.text("How successful are tailored resumes?")
            res1, res2 = st.columns(2, gap="medium", border=True)
            with res1:
                st.dataframe(resume_df, hide_index=True)
            with res2:
                st.text("This section measures the effectiveness of tailoring resumes to each job application.")

            # Cover Letter info
            st.html("<hr>")
            st.subheader("Cover Letter Details")
            st.text("How successful are cover letters?")
            cov1, cov2 = st.columns(2, gap="medium", border=True)
            with cov1:
                st.dataframe(cover_df, hide_index=True)
            with cov2:
                st.html(
                    "Status Breakdown:"
                    "<ul style='padding-left: 5%'>" \
                    "<li>Yes = Cover letter was sent.</li>" \
                    "<li>No = Cover letter was not sent.</li>" \
                    "<li>Unavailable = There was no place to add a cover letter on the application.</li>" \
                    "<li>Questionnaire = In leiu of a cover letter, there were short-answer response questions.</li>" \
                    "</ul>"
                )


    except:
        st.write("Something went wrong.")