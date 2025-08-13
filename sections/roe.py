import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
import altair as alt

# Homebrew files
import sections.constants as constants
from sections.methods import *

# Color constants
color1 = constants.COLOR1
color2 = constants.COLOR2
gradient = [color1, color2]
barcolor = "turbo"

def show(apps, roe):
    st.title("ROE Calculations")
    try:
        # ----------------------------------------------- Constants
        total_apps = apps[apps.columns[0]].dropna().count()
        apps_nopend = apps[apps["Status"].str.contains("Pending")==False]
        real_response_number = sum(1 for app_stat in apps_nopend["Status"].dropna() if app_stat in constants.REAL_RESP)
        real_response_rate = str('{0:.4g}'.format((real_response_number/total_apps)*100)) + "%"

        # ----------------------------------------------- Dataframes
        status_df = groupby_smaller(apps, "Role Type", "Status", "Applications In Status", "Applications In Status")

        # ----------------------------------------------- Calculations
        # Scatterplot colored by application status
        roe_formatted = roe.reset_index().rename(columns={"index": "Application Number"})
        # Get unique statuses from your data
        unique_statuses = roe_formatted["Application Status"].unique().tolist()
        # Drop the weird zero at the end if it exists
        if unique_statuses[len(unique_statuses)-1] == 0:
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
        st.text("Note: The return on effort charts all index from 0. Add 1 to find the real application number.")

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
            st.text("Application statuses are defined in the Glossary.")

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


    except:
        st.write("Something went wrong, check to make sure all columns are labeled correctly.")