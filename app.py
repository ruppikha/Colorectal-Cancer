import streamlit as st
import pandas as pd
import numpy as np
import pickle

# =========================
# LOAD MODEL + REFERENCE
# =========================
@st.cache_resource
def load_model():
    with open("cox_model.pkl", "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_reference():
    return pd.read_csv("train_reference.csv")

cph = load_model()
train_df = load_reference()

features = cph.params_.index

# =========================
# SIDEBAR INPUT
# =========================
st.sidebar.header("Patient Input")

age = st.sidebar.slider("Age", 20, 90, 50)
bmi = st.sidebar.slider("BMI", 15.0, 40.0, 25.0)

smoking = st.sidebar.selectbox("Smoking", ["No", "Former"])
alcohol = st.sidebar.selectbox("Alcohol", ["Low", "Medium"])
fiber = st.sidebar.selectbox("Fiber", ["Low", "Medium"])

region = st.sidebar.selectbox(
    "Region",
    ["North America", "Asia Pacific", "Latin America"]
)

# =========================
# BUILD INPUT VECTOR
# =========================
input_dict = {col: 0 for col in features}

input_dict["Age"] = age
input_dict["BMI"] = bmi

if "Smoking_Status_Former" in features and smoking == "Former":
    input_dict["Smoking_Status_Former"] = 1

if "Alcohol_Consumption_Medium" in features and alcohol == "Medium":
    input_dict["Alcohol_Consumption_Medium"] = 1

if "Fiber_Consumption_Low" in features and fiber == "Low":
    input_dict["Fiber_Consumption_Low"] = 1

if region == "North America" and "Region_North America" in features:
    input_dict["Region_North America"] = 1
elif region == "Asia Pacific" and "Region_Asia Pacific" in features:
    input_dict["Region_Asia Pacific"] = 1
elif region == "Latin America" and "Region_Latin America" in features:
    input_dict["Region_Latin America"] = 1

input_df = pd.DataFrame([input_dict])

# =========================
# RISK PREDICTION
# =========================
risk = cph.predict_partial_hazard(input_df).values[0]

# percentile (NO leakage)
all_risk = cph.predict_partial_hazard(train_df)
risk_percentile = (all_risk < risk).mean()

# risk group
if risk_percentile < 0.33:
    group = "Low Risk"
elif risk_percentile < 0.66:
    group = "Medium Risk"
else:
    group = "High Risk"

# =========================
# MAIN UI
# =========================
st.title("Colorectal Cancer Risk Dashboard")

st.metric("Risk Percentile", f"{risk_percentile:.2f}")
st.metric("Risk Group", group)

# =========================
# CONTRIBUTIONS (EXPLAINABILITY)
# =========================
st.subheader("Top Risk Drivers")

coefs = cph.params_
contributions = (input_df.iloc[0] * coefs)

# sort by absolute importance
contributions = contributions.reindex(
    contributions.abs().sort_values(ascending=False).index
)

top_features = contributions.head(10)

st.bar_chart(top_features)

# =========================
# SIMILAR PATIENTS
# =========================
st.subheader("Similar Patients")

subset = train_df[
    train_df["Age"].between(age - 5, age + 5)
]

subset_risk = cph.predict_partial_hazard(subset)

st.write("Average Risk (similar patients):", round(subset_risk.mean(), 3))

st.line_chart(np.sort(subset_risk.values))

# =========================
# WHAT-IF ANALYSIS
# =========================
st.subheader("What-if Analysis")

new_smoking = st.selectbox("Change Smoking", ["No", "Former"])

what_if = input_df.copy()

if "Smoking_Status_Former" in features:
    what_if["Smoking_Status_Former"] = 1 if new_smoking == "Former" else 0

new_risk = cph.predict_partial_hazard(what_if).values[0]

risk_change = new_risk - risk

st.write("New Risk:", round(new_risk, 3))
st.write("Risk Change:", round(risk_change, 3))