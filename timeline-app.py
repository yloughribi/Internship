# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import dask.dataframe as dd
import streamlit as st

# %%
diag = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\diagnoses_table.csv')

# %%

def detect_icd_version(code):
    code = str(code).strip().upper()
    return 10 if code and code[0].isalpha() else 9

# Apply to your DataFrame
diag['icd_version'] = diag['icd_code'].apply(detect_icd_version)
# %%
diag.head(10)

# %%
adm = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\admissions_table.csv')

# %%
adm.head(10)

# %%
diag_df = diag.merge(adm, on=['subject_id', 'hadm_id'])
diag_df = diag_df.sort_values(by="subject_id")

# %%
diag_df = diag_df.reset_index(drop=True)

# %%

nrows, ncols = diag_df.shape[0].compute(), len(diag_df.columns)

st.write(f"Shape: ({nrows}, {ncols})")

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
diag_df = diag_df.compute()

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