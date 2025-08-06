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

def show(apps, interviews):
    st.title("Interview Data")
    try:
        # ----------------------------------------------- Constants
        # Interview metrics
        num_interviewed_at = sum(1 for app_stat in apps["Status"].dropna() if app_stat in constants.REAL_RESP)
        currently_interviewing = sum(1 for app_stat in apps["Status"].dropna() if app_stat in ["Interviewing"])
        sum_interviews = interviews[interviews.columns[0]].dropna().count() # NOT sum of apps interview column cause duplicates

        num_weeks = apps["Week"].max() # Number of weeks for later calc

        avg_int_per_role = apps['Number of Interviews'].dropna().mean()

        interview_max = apps['Number of Interviews'].dropna().max()
        interview_max_company = apps.iloc[int(apps['Number of Interviews'].dropna().idxmax()), 0]

        # ----------------------------------------------- Dataframes
        weekly_df = groupby_percents(apps, "Week")
        if weekly_df.iloc[len(weekly_df)-1][0] < 0: # Drop extra auto values if they exist
            weekly_df = weekly_df.drop(0) 
        last_four_weeks = weekly_df['# of Applications'].head(4).sum()  

        # Multiple agg groupbys - can't use the function I made
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

        # ----------------------------------------------- Calculations
        st.header("Interviews")

        # Interview charts
        st.subheader("By the numbers:")
        matrix5, matrix6 = st.columns(2, border=True, gap="medium")
        with matrix5:
            st.subheader("Interviews by WEEK APPLIED:")
            chart = alt.Chart(weekly_df).mark_bar().encode(
                x=alt.X('Week:O', title='Week Number'),
                y=alt.Y('Interviews:Q', title='Number of Interviews'),
                tooltip=['Week', 'Interviews'],
                color=alt.value(color1)
            )
            st.altair_chart(chart, use_container_width=True)
            st.text("Note: This chart shows the number of interviews per week based on when the application was sent, not when the actual interview occured. This helps show how successful a resume is on any given week and how changes to a resume impact interviews.")
            st.text("There's usually a 2-3 week lag time in getting interviews due to response time turnaround.")   
        with matrix6:
            st.subheader("Number of interviews, by round:")
            round_chart = alt.Chart(just_round_df).mark_bar().encode(
                x=alt.X('Round:O', title='Round'),
                y=alt.Y('Number of Interviews:Q', title='Number of Interviews'),
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
            st.text("Note: The total interviews metric may not line up with the number of interviews reported in the 'Applications' spreadsheet. This is because interviews may be tagged to more than one role. For example, a company may use a first-round phone call to consider an applicant for two or more roles.")
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

    except:
        st.write("Something went wrong.\nTwo sheets are required for interview metrics: 'Tracker' and 'Interviews'. Please make sure you have sheets with those names!")