# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

# %%
diag = pd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV files\diagnoses_table.csv')

# %%
diag.head(10)

# %%
adm = pd.read_csv(r'C:\Users\Yahya\Documents\GitHub\Internship\CSV files\admissions_table.csv')

# %%
adm.head(10)

# %%
diag_df = diag.merge(adm, on=['subject_id', 'hadm_id'])

# %%
diag_df.head(10)

# %%
import streamlit as st
import pandas as pd
import plotly.express as px

# Load your combined CSV or DataFrame
df = diag_df.copy()

st.title("ICD Code Timeline by Subject")

# Optional: filter by subject_id or hadm_id
df['icd_version'] = df['icd_version'].astype(str)
df['icd_code'] = df['icd_code'].astype(str)


subject_ids = df['subject_id'].unique()
selected_subject = st.selectbox("Select Subject ID", subject_ids)

filtered_df = df[df['subject_id'] == selected_subject]

# Create timeline plot
fig = px.timeline(
    filtered_df,
    x_start="admittime",
    x_end="dischtime",
    y="hadm_id",
    text = "icd_code",
    color="icd_version",
    title=f"ICD Diagnosis Timeline for Subject {selected_subject}",
    hover_data=["hadm_id"]
)

fig.update_yaxes(autorange="reversed")  # Timeline style
st.plotly_chart(fig, use_container_width=True)


top_diag = df['icd_code'].value_counts().nlargest(20)
st.bar_chart(top_diag)

