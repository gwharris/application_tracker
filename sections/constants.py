"""
Constants.py
"""

DEFAULT_FILE = "example_app_tracker.xlsx"
REAL_FILE = "app_tracker.xlsx"

APPS_COLUMNS = [
    "Company",
    "Industry",
    "Role Type",
    "Date",
    "Salary Min",
    "Salary Max",
    "Platform",
    "Resume ID",
    "Cover Letter",
    "Company Size",
    "Status",
    "Response Date",
    "Response Time (Days)",
    "Number of Interviews",
    "Month",
    "Week"
]
INTERVIEW_COLUMNS = [
    "Company",
    "Role Type",
    "Date",
    "Round",
    "Type of Interview",
    "Location",
    "Performance",
    "Experience",
]
ROE_COLUMNS = [
    "Company Name",
    "Application Status",
    "Chance of Success",
    "Application Effort",
    "ROE"
]

ALL_RESP = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 
            'On Hold', 'Denied', 'Viewed', 'Offer', 'No Offer'] # Denied and Viewed are auto responses

REAL_RESP = ['Rejected', 'Bailed', 'Interviewing', 'Ghosted', 'On Hold', 'Offer', 'No Offer'] # So real != Denied, Viewed

COLOR1 = "#26bce1"
COLOR2 = "#4a58dd"