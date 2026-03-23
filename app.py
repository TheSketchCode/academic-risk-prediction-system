import streamlit as st
import joblib
import numpy as np
import sqlite3
import pandas as pd
import plotly.graph_objects as go

# Load trained ML model
model = joblib.load("model.pkl")

st.set_page_config(page_title="Academic Risk Dashboard", layout="wide")

st.title("📊 Academic Performance Risk Prediction System")
st.markdown("### Machine Learning Based Early Academic Risk Detection System")


# ➕ ADD NEW STUDENT SECTION


st.subheader("➕ Add New Student")

col1, col2 = st.columns(2)

with col1:
    new_name = st.text_input("Student Name")

with col2:
    new_attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, key="att")

col3, col4 = st.columns(2)

with col3:
    new_marks = st.number_input("Internal Marks", min_value=0, max_value=100, key="marks")

with col4:
    new_assignment = st.number_input("Assignment Completion (%)", min_value=0, max_value=100, key="assign")

if st.button("Add Student", key="add_btn"):

    if new_name.strip() == "":
        st.warning("Please enter student name.")
    else:
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students (name, attendance, internal_marks, assignment_completion)
        VALUES (?, ?, ?, ?)
        """, (new_name, new_attendance, new_marks, new_assignment))

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        st.success(f"Student added successfully! Assigned ID: {new_id}")

# 🔎 FETCH & PREDICT SECTION


st.subheader("🔎 Fetch Student & Predict Risk")

student_id = st.number_input("Enter Student ID", min_value=1, step=1)

if st.button("Fetch and Predict", key="fetch_btn"):

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    conn.close()

    if student:

        name = student[1]
        attendance = student[2]
        marks = student[3]
        assignment = student[4]

        st.markdown(f"### 👤 Student Name: {name}")
        st.write(f"Attendance: {attendance}%")
        st.write(f"Internal Marks: {marks}")
        st.write(f"Assignment Completion: {assignment}%")

        input_data = pd.DataFrame(
    [[attendance, marks, assignment]],
    columns=["Attendance", "InternalMarks", "AssignmentCompletion"]
)
        prediction = model.predict(input_data)
        probability = model.predict_proba(input_data)

        fail_prob = probability[0][list(model.classes_).index("Fail")] * 100
        pass_prob = probability[0][list(model.classes_).index("Pass")] * 100

        st.subheader("📈 Prediction Result")

        if prediction[0] == "Fail":
            st.error("⚠ High Risk of Failure")
        else:
            st.success("✅ Low Risk – Likely to Pass")

        st.write(f"Pass Probability: {round(pass_prob,2)}%")
        st.write(f"Fail Probability: {round(fail_prob,2)}%")

        # Probability Bar Chart
        fig = go.Figure(data=[
            go.Bar(name='Pass Probability', x=['Pass'], y=[pass_prob]),
            go.Bar(name='Fail Probability', x=['Fail'], y=[fail_prob])
        ])
        fig.update_layout(title="Probability Comparison", yaxis_title="Percentage")
        st.plotly_chart(fig, width="stretch")

        # Recommendations
        st.subheader("💡 Recommendations")

        if attendance < 75:
            st.write("• Improve attendance to at least 75%.")
        if marks < 50:
            st.write("• Focus more on internal preparation.")
        if assignment < 60:
            st.write("• Complete assignments regularly.")
        if attendance >= 75 and marks >= 50 and assignment >= 60:
            st.write("• Keep maintaining your current performance!")

    else:
        st.warning("Student not found.")

# 📊 DASHBOARD ANALYTICS


st.subheader("📊 Dashboard Analytics")

conn = sqlite3.connect("students.db")
df = pd.read_sql_query("SELECT * FROM students", conn)
conn.close()

if not df.empty:

    total_students = len(df)

    high_risk = 0
    low_risk = 0

    for index, row in df.iterrows():
        input_data = np.array([[row["attendance"], row["internal_marks"], row["assignment_completion"]]])
        pred = model.predict(input_data)

        if pred[0] == "Fail":
            high_risk += 1
        else:
            low_risk += 1

    colA, colB, colC = st.columns(3)

    colA.metric("Total Students", total_students)
    colB.metric("High Risk Students", high_risk)
    colC.metric("Low Risk Students", low_risk)

    # Pie Chart
    fig2 = go.Figure(data=[go.Pie(
        labels=['High Risk', 'Low Risk'],
        values=[high_risk, low_risk]
    )])

    fig2.update_layout(title="Overall Risk Distribution")
    st.plotly_chart(fig2, width="stretch")

# 📋 STUDENT DATABASE TABLE


st.subheader("📋 All Students Database")

if not df.empty:
    st.dataframe(df)
else:
    st.info("No student records found.")