import streamlit as st

def show():
    st.subheader("Known Issues")
    st.write("""
        Color picker doesn't work correctly.\n
        Error handling is broken and does not take into account wrong files being uploaded.\n
        Need to add handling for when only some columns are missing, not all.
    """)