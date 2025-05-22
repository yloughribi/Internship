# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

# %%
diag = pd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\diagnoses_table.csv')

# %%

def detect_icd_version(code):
    code = str(code).strip().upper()
    return 10 if code and code[0].isalpha() else 9

# Apply to your DataFrame
diag['icd_version'] = diag['icd_code'].apply(detect_icd_version)
# %%
diag.head(10)

# %%
adm = pd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\admissions_table.csv')

# %%
adm.head(10)

# %%
diag_df = diag.merge(adm, on=['subject_id', 'hadm_id'])

# %%
import streamlit as st
import pandas as pd
import plotly.express as px

# Load your combined CSV or DataFrame
df = diag_df.copy()

st.title("Visualization Patient Data MIMIC-IV dataset")

# Count the occurrences of each ICD code
diagnosis_counts = df['icd_code'].value_counts()

# Select the top 20 ICD codes
top_20_diagnoses = diagnosis_counts.head(20)

# Create a DataFrame for the top 20 ICD codes
top_20_df = top_20_diagnoses.reset_index()
top_20_df.columns = ['icd_code', 'count']

# Create bar chart
st.header("Top 20 ICD Codes")

fig = px.bar(
    top_20_df,
    x='icd_code',
    y='count',
    title="Top 20 ICD Codes by Count",
    labels={'icd_code': 'ICD Code', 'count': 'Count'}
)

fig.update_xaxes(type='category')

st.plotly_chart(fig, use_container_width=True)
# %%
diag_df.head(10)

import streamlit as st
import pandas as pd
import plotly.express as px

# Load your combined CSV or DataFrame
df = diag_df.copy()

# Optional: filter by subject_id or hadm_id
subject_ids = df['subject_id'].unique()
selected_subject = st.selectbox("Select Subject ID", subject_ids)

filtered_df = df[df['subject_id'] == selected_subject]

# Create timeline plot
st.header("Timeline Plot")

# Define a discrete color sequence for ICD versions
color_discrete_map = {
    'ICD-9': 'blue',
    'ICD-10': 'green'
}

fig = px.timeline(
    filtered_df,
    x_start="admittime",
    x_end="dischtime",
    y="icd_code",
    color="icd_version",
    title=f"ICD Diagnosis Timeline for Subject {selected_subject}",
    hover_data=["hadm_id"],
    color_discrete_map=color_discrete_map  # Apply the discrete color mapping
)

fig.update_yaxes(autorange="reversed", type='category')  # Timeline style
st.plotly_chart(fig, use_container_width=True)

# %%

import streamlit as st
import pandas as pd
import plotly.express as px

# Load your combined CSV or DataFrame
df = diag_df.copy()

# Convert 'admittime' and 'dischtime' to datetime
df['admittime'] = pd.to_datetime(df['admittime'])
df['dischtime'] = pd.to_datetime(df['dischtime'])

# Optional: filter by subject_id or hadm_id
subject_ids = df['subject_id'].unique()
selected_subject = st.selectbox("Select Subject ID", subject_ids, key='subject_select')

filtered_df = df[df['subject_id'] == selected_subject]

# Calculate length of stay
filtered_df['length_of_stay'] = (filtered_df['dischtime'] - filtered_df['admittime']).dt.days

# Create box plot
st.header("Box Plot of Admissions by ICD Code")

fig = px.box(
    filtered_df,
    x='icd_code',
    y='length_of_stay',  # Use the calculated length of stay
    color="icd_version",
    title=f"Box Plot of Admissions by ICD Code for Subject {selected_subject}",
    labels={'icd_code': 'ICD Code', 'length_of_stay': 'Length of Stay (days)'},
    color_discrete_map={
        'ICD-9': 'blue',
        'ICD-10': 'green'
    }
)

fig.update_xaxes(type='category')  # Ensure ICD codes are treated as categories
st.plotly_chart(fig, use_container_width=True)

# %%

import streamlit as st
import pandas as pd
import plotly.express as px

# Load your combined CSV or DataFrame
df = diag_df.copy()

# Sort the DataFrame by subject_id and admittime to identify readmissions
df = df.sort_values(by=['subject_id', 'admittime'])

# Identify readmissions: a readmission is any admission that is not the first for a given subject_id
df['is_readmission'] = df.duplicated('subject_id', keep='first')

# Filter readmissions
readmissions_df = df[df['is_readmission']]
# Count readmissions per ICD code
readmission_counts = readmissions_df['icd_code'].value_counts().reset_index()
readmission_counts.columns = ['icd_code', 'count']

readmission_counts = readmission_counts.head(15)

# Create bar chart
st.header("Readmission Patterns per ICD Code")

fig = px.bar(
    readmission_counts,
    x='icd_code',
    y='count',
    title="Readmission Patterns per ICD Code",
    labels={'icd_code': 'ICD Code', 'count': 'Number of Readmissions'}
)

# Set the x-axis type to 'category' to ensure ICD codes are displayed correctly
fig.update_xaxes(type='category')

st.plotly_chart(fig, use_container_width=True)

# %%

import pandas as pd
import plotly.express as px

# Sample data
data = {
    'Event': ['Restless legs', 'Hypertension', 'Insomnia', 'Falls', 'Small-vessel cerebrovascular disease',
              'Visual hallucinations', 'Constipation', 'Delirium', 'Memory impairment'],
    'Start': ['2010-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01',
              '2015-01-01', '2016-01-01', '2017-01-01', '2018-01-01'],
    'End': ['2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01', '2015-01-01',
            '2016-01-01', '2017-01-01', '2018-01-01', '2019-01-01'],
    'Age': [68, 71, 71, 74, 74, 74, 77, 77, 77],
    'Details': ['Sex: X, Ethnicity: Y', 'Hypertension', 'Insomnia', 'Falls', 'Small-vessel cerebrovascular disease',
                'Visual hallucinations', 'Constipation', 'Delirium', 'Memory impairment']
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert Start and End to datetime
df['Start'] = pd.to_datetime(df['Start'])
df['End'] = pd.to_datetime(df['End'])

# Create timeline plot
fig = px.timeline(
    df,
    x_start="Start",
    x_end="End",
    y="Event",
    text="Details",
    title="Patient Timeline",
    labels={'Event': 'Event', 'Start': 'Start Date', 'End': 'End Date'},
    color="Age"
)

fig.update_yaxes(autorange="reversed")  # Timeline style
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
