import streamlit as st
import pandas as pd
import os

# Import pages
from sections import intro
from sections import breakdown
from sections import interviews
from sections import roe
from sections import glossary
from sections import constants

DEFAULT_FILE = "excel/example_app_tracker.xlsx"
REAL_FILE = "excel/app_tracker.xlsx"

# Wide mode
st.set_page_config(layout="wide", page_title="Application Data")

# ---- Sidebar Navigation ----
header1, header2, header3 = st.columns([3,1,2], gap='large')
with header1:
    st.title("Job Application - Data Visualization")

    # Layer 1 Columns
    st.header("Graham Harris")
    st.text("Since I was laid off in April 2025, I've been hard at work applying to new roles. This project is a capstone presentation of all of the data I've collected showcasing my data visualization skills.")
    st.text("Example data is loaded on the public application - please ask for the master data set to see my actual application journey.")
    st.text("Choose the colors for the graphs:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color1 = st.color_picker("Color 1", constants.COLOR1)
    with c2:
        color2 = st.color_picker("Color 2:", constants.COLOR2)
    # CHART COLORS
    gradient = [color1, color2]
    barcolor = "turbo"

# Check if file exists. Throws error if file is not present
with header3:
# User upload
    st.write("#")
    uploaded_file = st.file_uploader(
        "Upload your own application tracker here:", 
        type=["xlsx", "xls"],
        accept_multiple_files=False)
    st.download_button(
        label="Don't have the template yet? Download it here!",
        data="csv",
        file_name=DEFAULT_FILE,
        mime="text/csv",
        icon=":material/download:",
    )
    # Load data
    if uploaded_file is not None:
        apps = pd.read_excel(uploaded_file, sheet_name="Tracker")
        calc = pd.read_excel(uploaded_file, sheet_name="ROE Calculation")
        interview = pd.read_excel(uploaded_file, sheet_name="Interviews")
        st.success("✅ Uploaded file.")
    elif os.path.exists(REAL_FILE):
        apps = pd.read_excel(REAL_FILE, sheet_name="Tracker")
        calc = pd.read_excel(REAL_FILE, sheet_name="ROE Calculation")
        interview = pd.read_excel(REAL_FILE, sheet_name="Interviews")
        st.info("ℹ️ Running app locally with app_tracker.xlsx.")
    else:
        apps = pd.read_excel(DEFAULT_FILE, sheet_name="Tracker")
        calc = pd.read_excel(DEFAULT_FILE, sheet_name="ROE Calculation")
        interview = pd.read_excel(DEFAULT_FILE, sheet_name="Interviews")
        st.warning("⚠️ Master data set not found. Using default example data. If you uploaded an Excel file, make sure you have 3 sheets named: Tracker, ROE Calculation, Interviews")
    
st.write("#")
st.html("<hr style='border: 5px solid black; border-radius: 5px'>")

# Navbar!
st.sidebar.title("Navigation")
pages = [
    "Introduction",
    "Application Data",
    "Interviews",
    "ROE",
    "Glossary"
]
page = st.sidebar.radio("Go to", pages)

# ---- Page Routing ----
if page == "Introduction":
    intro.show()

elif page == "Application Data":
    breakdown.show(apps)

elif page == "Interviews":
    interviews.show(apps, interview)

elif page == "ROE":
    roe.show(apps, calc)

elif page == "Glossary":
    glossary.show()

