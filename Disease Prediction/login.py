import sqlite3
import streamlit as st
import hashlib


from patient_dashboard import patient_page
from doctor_dashboard import doctor_dashboard

# Database setup
conn = sqlite3.connect('main_app.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    first_name TEXT,
    last_name TEXT,
    phone_number TEXT,
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
''')
conn.commit()

# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(first_name, last_name, phone_number, email, password, role):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        return "Email already exists!"
    
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (first_name, last_name, phone_number, email, password, role) VALUES (?, ?, ?, ?, ?, ?)",
              (first_name, last_name, phone_number, email, hashed_password, role))
    conn.commit()
    return "Registration successful! You can now log in."

def authenticate(email, password):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    
    if user:
        hashed_password = hash_password(password)
        if user[4] == hashed_password:
            return user[5]
        else:
            return "Incorrect password"
    else:
        return "User not found"

# UI pages
def login_page():
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        role = authenticate(email, password)
        
        if role == "doctor":
            st.session_state.logged_in = True
            st.session_state.role = "doctor"
            st.session_state.email = email
            st.success("Login successful as Doctor!")
            return True
        elif role == "patient":
            st.session_state.logged_in = True
            st.session_state.role = "patient"
            st.session_state.email = email
            st.success("Login successful as Patient!")
            return True
        else:
            st.error(role)
            return False

    if st.button("Don't have an account? Register here!"):
        st.session_state.current_page = "register"
    return False

def register_page():
    st.title("Register Page")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    phone_number = st.text_input("Phone Number")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.radio("Select Role", ["patient", "doctor"])
    
    if st.button("Register"):
        if not first_name or not last_name or not phone_number or not email or not password or not confirm_password:
            st.error("All fields are required!")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        else:
            result = register_user(first_name, last_name, phone_number, email, password, role)
            if "successful" in result:
                st.success(result)
                st.session_state.current_page = "login"
            else:
                st.error(result)

    if st.button("Already have an account? Login here!"):
        st.session_state.current_page = "login"

# Main function
def main():
    # Initialize session state if not already done
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If the user is logged in, directly show their respective dashboard
    if st.session_state.logged_in:
        if st.session_state.role == "doctor":
            doctor_dashboard()
        elif st.session_state.role == "patient":
            patient_page()

    else:
        if "current_page" not in st.session_state:
              st.session_state.current_page = st.query_params.get("page", "login")  # Default to login page

        if st.session_state.current_page == "login":
            if login_page():
                if st.session_state.role == "doctor":
                   doctor_dashboard()
                elif st.session_state.role == "patient":
                    patient_page()

        elif st.session_state.current_page == "register":
            register_page()

# Example pages for doctor and patient (you can add more content here)
#def doctor_page():
   
    #if st.button("Logout"):
        #logout()

#def patient_page():
    
   # if st.button("Logout"):
       # logout()

def logout():
    # Clear the session state and redirect to login page
    st.session_state.clear()
    st.session_state.current_page = "login"
    st.success("You have logged out successfully!")
if __name__ == "__main__":
    main()
