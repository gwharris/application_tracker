"""
Methods
"""
import constants
import pandas as pd

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
        All_Positive=('Status', count_status(constants.ALL_RESP)),
        Real_Positive=('Status', count_status(constants.REAL_RESP)),
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
