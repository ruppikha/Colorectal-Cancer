import streamlit as st
import pandas as pd
import numpy as np

# =========================
# RULE-BASED SCORING SYSTEM
# =========================

def calculate_risk(input_data):
    score = 0
    contributions = {}

    # AGE
    if input_data["Age"] >= 70:
        score += 25
        contributions["Age (70+)"] = 25
    elif input_data["Age"] >= 50:
        score += 15
        contributions["Age (50-69)"] = 15
    else:
        score += 5
        contributions["Age (<50)"] = 5

    # BMI
    if input_data["BMI"] >= 30:
        score += 15
        contributions["BMI (Obese)"] = 15
    elif input_data["BMI"] >= 25:
        score += 10
        contributions["BMI (Overweight)"] = 10
    else:
        contributions["BMI (Normal)"] = 0

    # SMOKING
    if input_data["Smoking"] == "Former":
        score += 10
        contributions["Smoking"] = 10

    # ALCOHOL
    if input_data["Alcohol"] == "Medium":
        score += 8
        contributions["Alcohol"] = 8

    # FIBER
    if input_data["Fiber"] == "Low":
        score += 12
        contributions["Low Fiber Diet"] = 12

    # FAMILY HISTORY
    if input_data["Family_History"] == "Yes":
        score += 20
        contributions["Family History"] = 20

    # PHYSICAL ACTIVITY
    if input_data["Physical_Activity"] == "Low":
        score += 10
        contributions["Low Activity"] = 10

    # RED MEAT
    if input_data["Red_Meat"] == "High":
        score += 10
        contributions["High Red Meat"] = 10

    return score, contributions


def risk_group(score):
    if score < 30:
        return "Low Risk"
    elif score < 60:
        return "Medium Risk"
    else:
        return "High Risk"


# =========================
# UI
# =========================

st.title("Colorectal Cancer Risk Dashboard (Rule-Based)")

st.sidebar.header("Patient Input")

age = st.sidebar.slider("Age", 20, 90, 50)
bmi = st.sidebar.slider("BMI", 15.0, 40.0, 25.0)

smoking = st.sidebar.selectbox("Smoking", ["No", "Former"])
alcohol = st.sidebar.selectbox("Alcohol", ["Low", "Medium"])
fiber = st.sidebar.selectbox("Fiber", ["Low", "Medium"])

family = st.sidebar.selectbox("Family History", ["No", "Yes"])
activity = st.sidebar.selectbox("Physical Activity", ["High", "Low"])
red_meat = st.sidebar.selectbox("Red Meat Consumption", ["Low", "High"])

# =========================
# BUILD INPUT
# =========================

input_data = {
    "Age": age,
    "BMI": bmi,
    "Smoking": smoking,
    "Alcohol": alcohol,
    "Fiber": fiber,
    "Family_History": family,
    "Physical_Activity": activity,
    "Red_Meat": red_meat
}

# =========================
# CALCULATE RISK
# =========================

score, contributions = calculate_risk(input_data)
group = risk_group(score)

# normalize score (0–100)
risk_percent = min(score, 100)

# =========================
# OUTPUT
# =========================

st.metric("Risk Score", f"{risk_percent}/100")
st.metric("Risk Group", group)

st.write(f"This patient falls into the **{group}** category based on rule-based assessment.")

# =========================
# CONTRIBUTIONS
# =========================
st.subheader("Risk Drivers")

if contributions:
    contrib_df = pd.DataFrame.from_dict(contributions, orient="index", columns=["Score"])
    contrib_df = contrib_df.sort_values(by="Score", ascending=True)
    st.bar_chart(contrib_df)
else:
    st.write("No major risk drivers identified.")

# =========================
# RULE-BASED EXPLANATION
# =========================
st.subheader("Explanation")

for factor, value in contributions.items():
    st.write(f"• {factor} adds +{value} risk points")

# =========================
# WHAT-IF ANALYSIS
# =========================
st.subheader("What-if Analysis")

new_smoking = st.selectbox("Change Smoking", ["No", "Former"], key="whatif")

what_if_input = input_data.copy()
what_if_input["Smoking"] = new_smoking

new_score, _ = calculate_risk(what_if_input)
change = new_score - score

st.write(f"New Score: {new_score}/100")
st.write(f"Change in Risk: {change:+}")