import sqlite3
import os

# Getting the working directory of the script
working_dir = os.path.dirname(os.path.abspath(__file__))

# Connect to the SQLite database
try:
    conn = sqlite3.connect(f"{working_dir}/main_app.db")
    cursor = conn.cursor()
    print("Connected to the database successfully.")
    
    # Query to select all data from the patient_data table
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    if rows:
        print("Data from users table:")
        for row in rows:
            print(row)
    else:
        print("No data found in the patient_data table.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("Connection closed.")