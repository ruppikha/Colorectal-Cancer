import streamlit as st
import pandas as pd
import numpy as np

# =========================
# LOAD DATA (FULL DATASET)
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("colorectal_cancer_prediction.csv")

df = load_data()

# =========================
# RISK RULES (INTERNAL ONLY)
# =========================
def compute_risk_row(row):
    score = 0

    if row["Age"] >= 70: score += 3
    elif row["Age"] >= 50: score += 2
    else: score += 1

    if row["BMI"] >= 30: score += 2
    elif row["BMI"] >= 25: score += 1

    if row["Smoking_Status"] == "Former": score += 1
    if row["Alcohol_Consumption"] == "Medium": score += 1
    if row["Fiber_Consumption"] == "Low": score += 2

    if row["Family_History"] == "Yes": score += 3
    if row["Previous_Cancer_History"] == "Yes": score += 3

    if row["Tumor_Aggressiveness"] == "High": score += 3
    if row["Screening_Regularity"] == "Irregular": score += 2

    if row["Physical_Activity_Level"] == "Low": score += 1
    if row["Red_Meat_Consumption"] == "High": score += 1

    return score

def risk_group(score):
    if score <= 4:
        return "Low"
    elif score <= 8:
        return "Medium"
    else:
        return "High"

# apply to dataset
df["risk_score"] = df.apply(compute_risk_row, axis=1)
df["risk_group"] = df["risk_score"].apply(risk_group)

# =========================
# USER INPUT
# =========================
st.title("Colorectal Cancer Risk Explorer")

st.sidebar.header("Patient Input")

input_data = {
    "Age": st.sidebar.slider("Age", 20, 90, 50),
    "Region": st.sidebar.selectbox("Region", df["Region"].unique()),
    "Race": st.sidebar.selectbox("Ethnicity", df["Race"].unique()),
    "BMI": st.sidebar.slider("BMI", 15.0, 40.0, 25.0),

    "Smoking_Status": st.sidebar.selectbox("Smoking", df["Smoking_Status"].unique()),
    "Alcohol_Consumption": st.sidebar.selectbox("Alcohol", df["Alcohol_Consumption"].unique()),
    "Fiber_Consumption": st.sidebar.selectbox("Fiber", df["Fiber_Consumption"].unique()),

    "Family_History": st.sidebar.selectbox("Family History", df["Family_History"].unique()),
    "Previous_Cancer_History": st.sidebar.selectbox("Previous Cancer", df["Previous_Cancer_History"].unique()),

    "Tumor_Aggressiveness": st.sidebar.selectbox("Tumor Aggressiveness", df["Tumor_Aggressiveness"].unique()),
    "Screening_Regularity": st.sidebar.selectbox("Screening", df["Screening_Regularity"].unique()),

    "Physical_Activity_Level": st.sidebar.selectbox("Activity", df["Physical_Activity_Level"].unique()),
    "Red_Meat_Consumption": st.sidebar.selectbox("Red Meat", df["Red_Meat_Consumption"].unique()),
}

# compute patient risk
patient_score = compute_risk_row(input_data)
patient_group = risk_group(patient_score)

# =========================
# OUTPUT (NO SCORE)
# =========================
st.subheader("Patient Risk Category")
st.success(f"{patient_group} Risk")

# =========================
# INTERACTIVE COMPARISON
# =========================
st.subheader("Compare with Similar Patients")

factor = st.selectbox(
    "Compare by:",
    ["Age", "Region", "Race", "Gender", "BMI"]
)

# build subset
subset = df.copy()

if factor == "Age":
    subset = df[df["Age"].between(input_data["Age"]-5, input_data["Age"]+5)]

elif factor == "Region":
    subset = df[df["Region"] == input_data["Region"]]

elif factor == "Race":
    subset = df[df["Race"] == input_data["Race"]]

elif factor == "BMI":
    subset = df[df["BMI"].between(input_data["BMI"]-3, input_data["BMI"]+3)]

# distribution
dist = subset["risk_group"].value_counts(normalize=True)

st.write("Distribution of risk in selected group:")
st.bar_chart(dist)

# highlight patient position
st.info(f"Patient falls into **{patient_group}** risk category in this group")

# =========================
# MULTI-FACTOR FILTER (ADVANCED)
# =========================
st.subheader("Refine Comparison")

use_multi = st.checkbox("Match multiple factors")

if use_multi:
    subset = df[
        (df["Age"].between(input_data["Age"]-5, input_data["Age"]+5)) &
        (df["Region"] == input_data["Region"]) &
        (df["Race"] == input_data["Race"])
    ]

    dist_multi = subset["risk_group"].value_counts(normalize=True)
    st.write("More precise comparison:")
    st.bar_chart(dist_multi)

# =========================
# WHAT-IF (ALL FACTORS)
# =========================
st.subheader("What-if Analysis (All Factors)")

what_if_factor = st.selectbox(
    "Change Factor",
    list(input_data.keys())
)

new_value = st.selectbox(
    "New Value",
    df[what_if_factor].unique() if what_if_factor != "Age" and what_if_factor != "BMI"
    else None
)

what_if_data = input_data.copy()

if what_if_factor in ["Age", "BMI"]:
    new_value = st.slider("New Value", 20, 90, input_data[what_if_factor])

what_if_data[what_if_factor] = new_value

new_group = risk_group(compute_risk_row(what_if_data))

st.write(f"New Risk Category: **{new_group}**")

# change explanation
if new_group != patient_group:
    st.warning(f"Risk changes from {patient_group} → {new_group}")
else:
    st.write("No change in risk category")

# =========================
# DRIVER EXPLANATION
# =========================
st.subheader("Key Risk Factors")

drivers = []

if input_data["Age"] >= 50: drivers.append("Age")
if input_data["BMI"] >= 25: drivers.append("BMI")
if input_data["Fiber_Consumption"] == "Low": drivers.append("Low Fiber")
if input_data["Family_History"] == "Yes": drivers.append("Family History")
if input_data["Smoking_Status"] == "Former": drivers.append("Smoking")

if drivers:
    for d in drivers:
        st.write(f"• {d} contributes to increased risk")
else:
    st.write("No major high-risk indicators")