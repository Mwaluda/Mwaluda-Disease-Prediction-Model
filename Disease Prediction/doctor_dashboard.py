import streamlit as st
import sqlite3
from fpdf import FPDF
import os

# Database connection
working_dir = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect("patients_data.db", check_same_thread=False)
cursor = conn.cursor()



def generate_pdf(patient_data, recommendations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Patient Diagnosis Report", ln=True, align='C')
    pdf.ln(10)

    # Add patient data
    for key, value in patient_data.items():
        pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, txt="Doctor's Recommendations:", ln=True)
    pdf.multi_cell(0, 10, txt=recommendations)

    # Save PDF file
    file_path = f"{working_dir}/reports/{patient_data['Name']}_report.pdf"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    pdf.output(file_path)
    return file_path

def doctor_dashboard():
    st.title("Doctor's Dashboard")

    # Fetch all patients from the database
    cursor.execute("SELECT DISTINCT name FROM patient_data")
    patient_names = [row[0] for row in cursor.fetchall()]
    
    if not patient_names:
        st.warning("No patient data available.")
        return

    # Select a patient
    selected_patient = st.selectbox("Select a Patient", patient_names)

    if selected_patient:
        # Fetch patient data for the selected patient
        cursor.execute("SELECT disease, diagnosis FROM patient_data WHERE name = ?", (selected_patient,))
        patient_records = cursor.fetchall()

        if patient_records:
            st.subheader(f"Data for {selected_patient}")
            
            # Display all records for the patient
            for i, (disease, diagnosis) in enumerate(patient_records, start=1):
                st.write(f"**Record {i}:**")
                st.write(f"- **Disease:** {disease}")
                st.write(f"- **Diagnosis:** {diagnosis}")
                st.write("---")

            # Allow doctor to add new recommendations
            st.subheader("Add Recommendations")
            new_recommendations = st.text_area("Enter your recommendations for the patient")

            # Generate Report Button
            if st.button("Generate Report"):
                patient_data = {
                    "Name": selected_patient,
                    "Disease": disease,
                    "Diagnosis": diagnosis
                }
                report_path = generate_pdf(patient_data, new_recommendations)
                st.success("Report generated successfully!")
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Download Report",
                        data=f,
                        file_name=f"{selected_patient}_report.pdf",
                        mime="application/pdf"
                    )

            # Save Recommendations Button
            if st.button("Save Recommendations"):
                cursor.execute("""
                    UPDATE patient_data 
                    SET recommendations = ? 
                    WHERE name = ? AND disease = ? AND diagnosis = ?""",
                    (new_recommendations, selected_patient, disease, diagnosis)
                )
                conn.commit()
                st.success("Recommendations saved successfully!")

    # Logout button
    if st.button('Logout'):
        st.session_state.clear()  # Clear session state
        st.success("You have been logged out. Redirecting to login page...")
        # Here you can redirect to the login page, for example:
        st.rerun()  # This will rerun the app, and you can handle the login logic in the main app

if __name__ == "__main__":
    doctor_dashboard()


 # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"