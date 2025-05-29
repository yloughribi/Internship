# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import dask.dataframe as dd
import streamlit as st

# %%
diag = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\diagnoses_table.csv', dtype={'icd_code': 'object'})

# %%

def detect_icd_version(code):
    code = str(code).strip().upper()
    return 10 if code and code[0].isalpha() else 9

# Apply to your DataFrame
diag['icd_version'] = diag['icd_code'].apply(detect_icd_version, meta=('icd_version', 'int64'))
# %%
diag.head(10)

# %%
adm = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\admissions_table.csv')

# %%
adm.head(10)

# %%
diag_df = diag.merge(adm, on=['subject_id', 'hadm_id'])

# %%

icd_d = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\icd_details.csv', dtype={'icd_code': 'object'})

#%%

diag_df['icd_code'] = diag_df['icd_code'].astype(str)
icd_d['icd_code'] = icd_d['icd_code'].astype(str)

icd_d['icd_version'] = icd_d['icd_version'].astype(int)

#%%

diag_df = diag_df.merge(icd_d, on=['icd_code', 'icd_version'])
#%%

diag_df = diag_df.sort_values(by="subject_id")

# %%
diag_df = diag_df.reset_index(drop=True)

#%%

st.write(diag_df.columns)

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

#%%

import streamlit as st
import dask.dataframe as dd
import pandas as pd
import tempfile
import os

@st.cache_data
def load_data():
    diag_dask = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\diagnoses_table.csv', dtype={'icd_code': 'object'})
    adm_dask = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\admissions_table.csv')
    diag_d_dask = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\icd_details.csv', dtype={'icd_code': 'object'})
    
    # Convert datetime columns
    adm_dask["admittime"] = dd.to_datetime(adm_dask["admittime"])
    adm_dask["dischtime"] = dd.to_datetime(adm_dask["dischtime"])

    # Merge and return Dask DataFrames
    diag_df = diag_dask.merge(adm_dask, on=["subject_id", "hadm_id"])
    diag_df['icd_code'] = diag_df['icd_code'].astype(str)
    icd_d['icd_code'] = icd_d['icd_code'].astype(str)
    icd_d['icd_version'] = icd_d['icd_version'].astype(int)
    diag_df = diag_df.merge(icd_d, on=['icd_code', 'icd_version'])
    
    # Load lab table
    lab_df = dd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV_files\labevents_combined.csv')
    lab_df["charttime"] = dd.to_datetime(lab_df["charttime"])

    return diag_df, lab_df

diag_df_dask, lab_df_dask = load_data()

# --- Subject ID selection ---
@st.cache_data
def get_subject_ids(_df_dask):
    # Don't use .compute() on a Series — do it on full df first
    df = _df_dask[["subject_id"]].drop_duplicates().compute()
    df = df.sort_values("subject_id")
    return df["subject_id"].tolist()

subject_ids = get_subject_ids(diag_df_dask)
selected_id = st.selectbox("Select a subject_id", subject_ids)

# --- Generate timeline only when a subject is selected ---
if selected_id:
    st.write(f"Generating timeline for subject_id: {selected_id}")

    # Filter and compute data
    diag_df = diag_df_dask[diag_df_dask["subject_id"] == selected_id].compute()
    lab_df = lab_df_dask[lab_df_dask["subject_id"] == selected_id].compute()

    # Timeline for diagnoses
    diag_df['Start Date'] = pd.to_datetime(diag_df['admittime']).dt.strftime('%Y-%m-%d')
    diag_df['End Date'] = pd.to_datetime(diag_df['dischtime']).dt.strftime('%Y-%m-%d')
    diag_df['Headline'] = "Diagnosis: " + diag_df['icd_code'].astype(str) + " = " + diag_df['long_title'].astype(str)
    diag_df['Text'] = "ICD Version: " + diag_df['icd_version'].astype(str)
    diag_df['Group'] = "Diagnosis"
    diag_df['Media'] = ""
    diag_df['Media Credit'] = ""
    diag_df['Media Caption'] = ""
    diag_df['Type'] = ""

    diag_timeline = diag_df[["Start Date", "End Date", "Headline", "Text", "Media", "Media Credit", "Media Caption", "Group", "Type"]]

    # Timeline for labs
    lab_grouped = (
        lab_df
        .groupby("hadm_id")
        .apply(
            lambda df: pd.Series({
                "Start Date": df["charttime"].min().strftime('%Y-%m-%d'),
                "End Date": "",  # Optional
                "Headline": f"Lab Results for Admission {df['hadm_id'].iloc[0]}",
                "Text": "<br>".join(
                    f"{row['label']}: {row['valuenum']} {row['valueuom'] or ''}"
                    for _, row in df.iterrows()
                ),
                "Group": "Lab",
                "Media": "",
                "Media Credit": "",
                "Media Caption": "",
                "Type": ""
            })
        )
        .reset_index(drop=True)
    )
    
    lab_timeline = lab_grouped[["Start Date", "End Date", "Headline", "Text", "Media", "Media Credit", "Media Caption", "Group", "Type"]]

    # Combine both timelines
    full_timeline = pd.concat([diag_timeline, lab_timeline], ignore_index=True)
    full_timeline.sort_values(by="Start Date", inplace=True)


    # Temporary file to store CSV
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, f"timeline_subject_{selected_id}.csv")
        full_timeline.to_csv(filepath, index=False)

        with open(filepath, "rb") as f:
            st.download_button(
                label="Download Timeline CSV",
                data=f.read(),
                file_name=f"timeline_subject_{selected_id}.csv",
                mime="text/csv"
            )

    st.success("Timeline generated and cleaned up!")

    #%%

    import streamlit.components.v1 as components

timeline_url = "https://cdn.knightlab.com/libs/timeline3/latest/embed/index.html?source=https://docs.google.com/spreadsheets/d/e/2PACX-1vT5GgFiacllGGuvYAaKdPXAji3otj7n4bqOaYIiwZSas2uHHGIUjuo92efkXiL2xG2o3szpSwkAXStw/pubhtml&font=Default&lang=en&initial_zoom=2&height=650"

components.iframe(timeline_url, height=650, scrolling=True)
