"""
Methods
"""
import sections.constants as constants
import pandas as pd

# ---------------------------------------- FUNCTIONS

# Validates if the correc information is in the passed excel
def validate_excel_headers(col_names, required_columns):
    """
    Validates headers in an Excel sheet.
    
    Returns:
        dict: Keys are headers (required or extra),
              Values are:
                - True if required and present
                - False if required and missing
                - "extra" if present but not required
    """
    # 1. Validate required headers
    header_status = {col: (col in col_names) for col in required_columns}
    
    # 2. Add extra headers
    for col in col_names:
        if col not in required_columns:
            header_status[col] = "extra"
    
    return header_status


# Takes the Excel structure and returns a formatted df
def convert_to_st(df: pd.DataFrame, x: str, y: str):
    x_side = df[x].dropna().astype(int)
    y_side = df[y][0:len(x_side)]
    new_df = pd.DataFrame({
        x: x_side.values,
        y: y_side.values
    })
    return new_df

# Used to count the valid responses in the Constants file
def count_status(status_list):
    return lambda x: x.isin(status_list).sum()

# Returns a df in the right formatting
def groupby_percents(sheet, col_name):
    """
    Formats the dataframes into groupable insights.

    Args:
        sheet: The Excel sheet to read, expects a dataframe
        col_name: The column to group on
    """
    return_df = sheet.groupby(col_name).agg(
        Applications=('Status', 'count'),
        Companies=('Company', pd.Series.nunique),
        Interviews=('Number of Interviews', 'sum'),
        Salary_Min=('Salary Min', 'mean'),
        Salary_Max=('Salary Max', 'mean'),
        All_Positive=('Status', count_status(constants.ALL_RESP)),
        Real_Positive=('Status', count_status(constants.REAL_RESP)),
        Response_Time=('Response Time (Days)', 'mean')
    ).reset_index().sort_values("Applications", ascending=False)

    # Calculate response % columns
    return_df['Total Responses'] = return_df['All_Positive'] / return_df['Applications'] * 100
    return_df['Total Responses'] = return_df['Total Responses'].apply('{:.1f}%'.format)
    return_df['Real Responses'] = return_df['Real_Positive'] / return_df['Applications'] * 100
    return_df['Real Responses'] = return_df['Real Responses'].apply('{:.1f}%'.format)

    # Calculate salary and response columns
    return_df['Salary_Min'] = return_df['Salary_Min'].apply('${:.2f}'.format)
    return_df['Salary_Max'] = return_df['Salary_Max'].apply('${:.2f}'.format)
    return_df['Response_Time'] = return_df['Response_Time'].apply('{:.2f}'.format)

    # Drop calculation columns
    return_df = return_df.drop('All_Positive', axis=1)
    return_df = return_df.drop('Real_Positive', axis=1)
    # Rename columns to more intuitive things
    return_df = return_df.rename(columns={
        'Applications': '# of Applications',
        'Companies': '# of Companies',
        'Salary_Min': 'Avg Min K',
        'Salary_Max': 'Avg Max K',
        'Response_Time': 'Avg DTR'
    })

    return return_df

# For DFs that need less groupby fields
def groupby_smaller(sheet, count, col_name, rename, sort):
    return_df = sheet.groupby(col_name).agg({
        count: 'count',
        'Number of Interviews': 'sum',
        'Response Time (Days)': 'mean'
    }).rename(columns={
        count: rename
    }).reset_index().sort_values(sort, ascending=False)
    return return_df

# Returns text that layers on top of a bar
def bar_text(chart, dy_val, quantity, prefix=None, datatype="N"):
    """
    Adds smart bar labels to an Altair chart.
    
    Args:
        chart: Altair bar chart
        dy_above: Vertical offset for text on top of bars
        quantity: The quantity to add to the top of bars
        prefix: Optional prefix for label (e.g., 'R:'), defaults to first letter of field
        datatype: Altair type ('N' nominal/string, 'Q' quantitative), default N to chart response rates which are strings
    """
    prefix = prefix or quantity[0].upper()

    return chart.mark_text(
        align='center',
        baseline='bottom',
        dy=dy_val  # height of the text
    ).transform_calculate(
        label=f"'{prefix}: ' + datum['{quantity}']"
    ).encode(
        text='label:' + datatype
    )