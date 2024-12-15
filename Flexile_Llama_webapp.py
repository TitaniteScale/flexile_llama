
# Flexile_Llama_webapp.py
# The main file for the Flexile Llama Streamlit app.

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from streamlit_authenticator import Authenticate

# Connect to the database
conn = sqlite3.connect('flexile_llama.db')  # Database for storing match data
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT,
    kills INTEGER,
    score INTEGER,
    match_date TEXT
)
''')
conn.commit()

# Streamlit App
st.title("Flexile Llama Performance Tracker")
st.markdown("### Track your Fortnite performance over time!")

# Configuring Authentication with Dummy Password
credentials = {
    "usernames": {
        "user": {
            "name": "User",
            "password": "dummy_password"
        }
    }
}

authenticator = Authenticate(credentials, "flexile_llama", "abcdef", cookie_expiry_days=30)

# Hide Password Field
hide_password = """
    <style>
        div[data-testid="stTextInput"] label:has(span:contains("Password")) {
            display: none !important;
        }
        div[data-testid="stTextInput"] input[type="password"] {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_password, unsafe_allow_html=True)

# Login Handling
name, authentication_status, username = authenticator.login(location="sidebar")
if authentication_status:
    st.sidebar.title(f"Welcome, {name}!")
    if st.sidebar.button("Logout"):
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success("You have logged out successfully!")

    # Add a Form for Manual Data Entry
    st.subheader("Add Match Data to Flexile Llama")

    with st.form("match_input_form"):
        mode = st.selectbox("Game Mode", ["Solo", "Duos", "Trios", "Squads"])
        kills = st.number_input("Number of Kills", min_value=0, step=1)
        score = st.number_input("Score", min_value=0, step=1)
        match_date = st.date_input("Match Date", value=date.today())
        submitted = st.form_submit_button("Submit Match Data")

        if submitted:
            # Insert the data into the database
            cursor.execute('INSERT INTO matches (mode, kills, score, match_date) VALUES (?, ?, ?, ?)', (mode, kills, score, str(match_date)))
            conn.commit()
            st.success("Match data has been successfully added to Flexile Llama!")

    # Upload a CSV File to Add Match Data in Bulk
    st.subheader("Upload Match Data in Bulk")

    uploaded_file = st.file_uploader("Choose a CSV file to upload", type=["csv"], key="csv_upload_button")

    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            bulk_data = pd.read_csv(uploaded_file)

            # Check if required columns exist
            required_columns = {"mode", "kills", "score", "match_date"}
            if required_columns.issubset(bulk_data.columns):
                # Insert data into the database
                for _, row in bulk_data.iterrows():
                    cursor.execute(
                        "INSERT INTO matches (mode, kills, score, match_date) VALUES (?, ?, ?, ?)",
                        (row["mode"], row["kills"], row["score"], row["match_date"]),
                    )
                conn.commit()
                st.success("Match data has been successfully uploaded!")
            else:
                st.error(
                    f"Error: The uploaded CSV must include the following columns: {', '.join(required_columns)}"
                )
        except Exception as e:
            st.error(f"An error occurred while processing the CSV: {e}")

    # Display Saved Data
    st.subheader("Saved Match Data")
    data = pd.read_sql_query("SELECT * FROM matches", conn)  # Fetch data from the database

    if not data.empty:
        st.write(data)  # Display data as a table

        # Visualization: Performance Over Time
        st.subheader("Performance Over Time")
        fig, ax = plt.subplots()
        ax.plot(data.index, data['kills'], label='Kills', marker='o')
        ax.plot(data.index, data['score'], label='Score', marker='x')
        ax.set_title("Kills and Scores Over Time")
        ax.set_xlabel("Match Index")
        ax.set_ylabel("Count")
        ax.legend()
        st.pyplot(fig)

        # Visualization: Mode Breakdown
        st.subheader("Mode Breakdown")
        mode_counts = data['mode'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(mode_counts.index, mode_counts.values)
        ax2.set_title("Games Played by Mode")
        ax2.set_xlabel("Mode")
        ax2.set_ylabel("Number of Games")
        ax2.set_xticklabels(mode_counts.index, rotation=45, ha="right")
        st.pyplot(fig2)
    else:
        st.write("No match data available. Add some matches to see your stats!")

else:
    if authentication_status is False:
        st.error("Username/password is incorrect.")
    elif authentication_status is None:
        st.warning("Please enter your username")

# Close the connection
conn.close()
