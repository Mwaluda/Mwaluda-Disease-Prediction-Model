import streamlit as st
from streamlit_option_menu import option_menu
import pickle
import sqlite3
import os

# Getting the working directory of the main.py
working_dir = os.path.dirname(os.path.abspath(__file__))

# Database connection with error handling
try:
    conn = sqlite3.connect(f"{working_dir}/patients_data.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Create the table if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        disease TEXT,
        diagnosis TEXT
    )
    """)
    conn.commit()
    st.success("Database connected and table created successfully.")
    
except sqlite3.Error as e:
    st.error(f"Database connection error: {e}")
    conn = None  # Set conn to None to prevent further operations if the connection fails

# Loading the saved models
try:
    diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
    heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
    parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))
except Exception as e:
    st.error(f"Error loading models: {e}")

def patient_page():
    if conn is None:
        st.error("Could not connect to the database. Please check your setup.")
        return  # Exit the function if the connection is not valid

    # Initialize session state variables
    if 'diabetes_diagnosis' not in st.session_state:
        st.session_state.diabetes_diagnosis = None
    if 'heart_disease_diagnosis' not in st.session_state:
        st.session_state.heart_disease_diagnosis = None
    if 'parkinsons_diagnosis' not in st.session_state:
        st.session_state.parkinsons_diagnosis = None

    st.title("Disease Prediction System")

    # Sidebar for disease selection
    with st.sidebar:
        selected = option_menu(
            'Disease Prediction Options',
            ['Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction'],
            icons=['activity', 'heart', 'person'],
            menu_icon='hospital',
            default_index=0
        )
    
    # Diabetes Prediction
    if selected == 'Diabetes Prediction':
        st.title('Diabetes Prediction using ML')
        name = st.text_input("Patient Name (Diabetes)", placeholder="Enter patient's full name")

        # Input fields
        col1, col2, col3 = st.columns(3)
        Pregnancies = col1.number_input('Number of Pregnancies', min_value=0, step=1)
        Glucose = col2.number_input('Glucose Level', min_value=0, step=1)
        BloodPressure = col3.number_input('Blood Pressure', min_value=0, step=1)
        SkinThickness = col1.number_input('Skin Thickness', min_value=0, step=1)
        Insulin = col2.number_input('Insulin Level', min_value=0, step=1)
        BMI = col3.number_input('BMI', min_value=0.0, step=0.1)
        DiabetesPedigreeFunction = col1.number_input('Diabetes Pedigree Function', value=0.078, step=0.001)
        Age = col2.number_input('Age', min_value=1, step=1)

        if st.button('Diabetes Test Result'):
            try:
                user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]
                prediction = diabetes_model.predict([user_input])
                st.session_state.diabetes_diagnosis = 'The person is diabetic' if prediction[0] == 1 else 'The person is not diabetic'
                st.success(st .session_state.diabetes_diagnosis)
            except Exception as e:
                st.error(f"Prediction error: {e}")

        if st.button('Submit Diabetes Data', disabled=(not name or st.session_state.diabetes_diagnosis is None)):
            if name and st.session_state.diabetes_diagnosis:
                try:
                    cursor.execute("INSERT INTO patient_data (name, disease, diagnosis) VALUES (?, ?, ?)", 
                                   (name, 'Diabetes', st.session_state.diabetes_diagnosis))
                    conn.commit()
                    st.success(f"Data for {name} saved successfully!")
                except sqlite3.Error as e:
                    st.error(f"Error saving data: {e}")
            else:
                st.error("Please provide the patient's name and run the diagnosis first.")

    # Heart Disease Prediction
    elif selected == 'Heart Disease Prediction':
        st.title('Heart Disease Prediction using ML')
        name = st.text_input("Patient Name (Heart Disease)", placeholder="Enter patient's full name")

        # Input fields
        col1, col2, col3 = st.columns(3)
        age = col1.number_input('Age', min_value=1, step=1, key='age_input')
        sex = col2.selectbox('Sex', options=['Male', 'Female'], key='sex_input')
        cp = col3.selectbox('Chest Pain Type', options=[0, 1, 2, 3], key='cp_input')
        trestbps = col1.number_input('Resting Blood Pressure', min_value=0, step=1, key='trestbps_input')
        chol = col2.number_input('Cholesterol', min_value=0, step=1, key='chol_input')
        fbs = col3.selectbox('Fasting Blood Sugar > 120 mg/dl', options=[0, 1], key='fbs_input')
        restecg = col1.selectbox('Resting Electrocardiographic Results', options=[0, 1, 2], key='restecg_input')
        thalach = col2.number_input('Maximum Heart Rate Achieved', min_value=0, step=1, key='thalach_input')
        exang = col3.selectbox('Exercise Induced Angina', options=[0, 1], key='exang_input')
        oldpeak = col1.number_input('Oldpeak', min_value=0.0, step=0.1, key='oldpeak_input')
        slope = col2.selectbox('Slope of the Peak Exercise ST Segment', options=[0, 1, 2], key='slope_input')
        ca = col3.number_input('Number of Major Vessels (0-3)', min_value=0, max_value=3, step=1, key='ca_input')
        thal = col1.selectbox('Thalassemia', options=[0, 1, 2, 3], key='thal_input')

        # Button to get test result
        if st.button('Heart Disease Test Result'):
            try:
                user_input = [
                    age, 
                    1 if sex == 'Male' else 0, 
                    cp, 
                    trestbps, 
                    chol, 
                    fbs, 
                    restecg, 
                    thalach, 
                    exang, 
                    oldpeak, 
                    slope, 
                    ca, 
                    thal
                ]
                prediction = heart_disease_model.predict([user_input])
                st.session_state.heart_disease_diagnosis = 'The person has heart disease' if prediction[0] == 1 else 'The person does not have heart disease'
                st.success(st.session_state.heart_disease_diagnosis)
            except Exception as e:
                st.error(f"Prediction error: {e}")

        # Submit button for saving data
        if st.button('Submit Heart Disease Data', disabled=(not name or st.session_state.heart_disease_diagnosis is None)):
            if name and st.session_state.heart_disease_diagnosis:
                try:
                    cursor.execute("INSERT INTO patient_data (name, disease, diagnosis) VALUES (?, ?, ?)", 
                                   (name, 'Heart Disease', st.session_state.heart_disease_diagnosis))
                    conn.commit()
                    st.success(f"Data for {name} saved successfully!")
                except sqlite3.Error as e:
                    st.error(f"Error saving data: {e}")
            else:
                st.error("Please provide the patient's name and run the diagnosis first.")

    # Parkinsons Prediction
    elif selected == 'Parkinsons Prediction':
        st.title('Parkinsons Prediction using ML')
        name = st.text_input("Patient Name (Parkinsons)", placeholder="Enter patient's full name")

        # Input fields
        col1, col2, col3 = st.columns(3)
        feature1 = col1.number_input('MDVP:Fo(Hz)', min_value=88.333, max_value=260.105, value=100.0)
        feature2 = col2.number_input('MDVP:Fhi(Hz)', min_value=102.145, max_value=592.03, value=150.0)
        feature3 = col3.number_input('MDVP:Flo(Hz)', min_value=65.476, max_value=239.17, value=70.0)
        feature4 = col1.number_input('MDVP:Jitter(%)', min_value=0.00168, max_value=0.03316, value=0.02)
        feature5 = col2.number_input('MDVP:Jitter(Abs)', min_value=0.000007, max_value=0.00026, value=0.0001)
        feature6 = col3.number_input('MDVP:RAP', min_value=0.00068, max_value=0.02144, value=0.001)
        feature7 = col1.number_input('MDVP:PPQ', min_value=0.00092, max_value=0.01958, value=0.001)
        feature8 = col2.number_input('Jitter:DDP', min_value=0.00204, max_value=0.06433, value=0.01)
        feature9 = col3.number_input('MDVP:Shimmer', min_value=0.00954, max_value=0.11908, value=0.01)
        feature10 = col1.number_input('MDVP:Shimmer(dB)', min_value=0.085, max_value=1.302, value=0.1)
        feature11 = col2.number_input('Shimmer:APQ3', min_value=0.00455, max_value=0.05647, value=0.01)
        feature12 = col3.number_input('Shimmer:APQ5', min_value=0.0057, max_value=0.0794, value=0.01)
        feature13 = col1.number_input('MDVP:APQ', min_value=0.00719, max_value=0.13778, value=0.01)
        feature14 = col2.number_input('Shimmer:DDA', min_value=0.01364, max_value=0.16942, value=0.015)
        feature15 = col3.number_input('NHR', min_value=0.00065, max_value=0.31482, value=0.01)
        feature16 = col1.number_input('HNR', min_value=8.441, max_value=33.047, value=10.0)
        feature17 = col2.number_input('RPDE', min_value=0.25657, max_value=0.685151, value=0.5)
        feature18 = col3.number_input('DFA', min_value=0.574282, max_value=0.825288, value=0.6)
        feature19 = col1.number_input('spread1', min_value=-7.964984, max_value=-2.434031, value=-5.0)
        feature20 = col2.number_input('spread2', min_value=0.006274, max_value=0.450493, value=0.1)
        feature21 = col3.number_input('D2', min_value=1.423287, max_value=3.671155, value=2.0)
        feature22 = col1.number_input('PPE', min_value=0.044539, max_value=0.527367, value=0.1)

        if st.button('Parkinsons Test Result'):
            try:
                user_input = [feature1, feature2, feature3, feature4, feature5, feature6, feature7, feature8, feature9, feature10,
                              feature11, feature12, feature13, feature14, feature15, feature16, feature17, feature18, feature19, feature20,
                              feature21, feature22]
                prediction = parkinsons_model.predict([user_input])
                st.session_state.parkinsons_diagnosis = 'The person has Parkinsons disease' if prediction[0] == 1 else 'The person does not have Parkinsons disease'
                st.success(st.session_state.parkinsons_diagnosis)
            except Exception as e:
                st.error(f"Prediction error: {e}")

        if st.button('Submit Parkinsons Data', disabled=(not name or st.session_state.parkinsons_diagnosis is None)):
            if name and st.session_state .parkinsons_diagnosis:
                try:
                    cursor.execute("INSERT INTO patient_data (name, disease, diagnosis) VALUES (?, ?, ?)", 
                                   (name, 'Parkinsons', st.session_state.parkinsons_diagnosis))
                    conn.commit()
                    st.success(f"Data for {name} saved successfully!")
                except sqlite3.Error as e:
                    st.error(f"Error saving data: {e}")
            else:
                st.error("Please provide the patient's name and run the diagnosis first.")

    # Logout button
    if st.button('Logout'):
        st.session_state.clear()  # Clear session state
        st.success("You have been logged out. Redirecting to login page...")
        # Here you can redirect to the login page, for example:
        st.rerun()  # This will rerun the app, and you can handle the login logic in the main app

# Run the patient page function
if __name__ == '__main__':
    patient_page()

# Close the database connection when the app ends
#if conn:
#    conn.close()