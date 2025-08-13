import streamlit as st

def show():
    st.title("Glossary")
    sizing1, sizing2 = st.columns([3,2])
    with sizing1:
        st.metric("Days To Respond - a response is measured on the first contact after an application is sent.", "DTR", border=True)
        st.metric("Not A Number - default value for when a data point cannot be calculated.", "nan", border=True)
        st.metric("Quantified experience of interviewing. Loosely measures how well the interviewers did at conducting the interview.", "Experience", border=True)
        st.metric("Percieved performance during an interview. Basically a difficulty/confidence score.", "Performance", border=True)
        st.html(
            "<p>Note: the response keywords are customizable and only apply to Graham's original dataset.</p>"\
            "<p>List of Valid Responses</p>"\
            "<ul style='padding-left: 5%'>" \
                "<li>Bailed - I lost interest in the role after interviewing.</li>" \
                "<li>Ghosted - The company stopped responding after I was interviewed.</li>" \
                "<li>Interviewing - Currently being interviewed.</li>" \
                "<li>No Offer - I completed all of the interview rounds and something prevented the company from sending an offer (they chose another candidate, budget for the role was revoked, etc.).</li>" \
                "<li>Offer - The company sent an offer.</li>" \
                "<li>On Hold - Something is blocking the application from moving forward (ie. a hiring freeze).</li>" \
                "<li>Rejected - Someone at the company directly reached out to deny my application (usually after interviewing).</li>" \
                "<li>Selected Out - I applied to multiple roles, then a recruiter reached out and asked me to pursue just one of them and not the others.</li>" \
            "</ul>"\
            "List of Invalid Responses"\
            "<ul style='padding-left: 5%'>" \
                "<li>Closed - The platform I applied on sent a notification that the role is no longer accepting applicants, which likely means they started the process and I was not chosen.</li>" \
                "<li>Denied - I received an automated denial.</li>" \
                "<li>Viewed - I received a notification that my application was viewed by a platform but the company did not connect with me (ie. LinkedIn sent a message that my application was seen but the company did not send any communication).</li>" \
            "</ul>"\
        )