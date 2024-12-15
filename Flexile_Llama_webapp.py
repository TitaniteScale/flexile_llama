# Flexile Llama: Fortnite Performance Tracker

# Goals:
# 1. Create a form-based model for manual data entry.
# 2. Integrate TRN API (pending access) for automated updates.
# 3. Add customizable thresholds for highlighting standout games.
# 4. Enable AI-based data extraction from match screenshots.
# 5. Deploy as a web-based app for cross-platform access (forego desktop/iPhone packaging for now).
# 6. Implement simple user identification (username-only) to allow personalized dashboards.

# Current Progress:
# - Initial dashboard set up with CSV-based data handling.
# - Basic analytics implemented.
# - Integrated a database (SQLite) for storing match data.
# - Developed a Streamlit app for tracking and visualizing performance.

# Next Steps:
# 1. Host the app on Streamlit Cloud for easy web access.
# 2. Ensure responsive design for mobile and desktop devices.
# 3. Add username-based identification to isolate data per user.
# 4. Prepare for TRN API integration to automate data fetching.

# Modules to Explore:
# - Pandas for analytics
# - OpenCV or Tesseract for screenshot data extraction
# - Streamlit Cloud for web hosting
# - Google Sheets API or Firebase for persistent user-specific storage

# Starting Point: Streamlit App with Username-Based Identification

# Flexile Llama Streamlit Code
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# --- SIMPLE USER IDENTIFICATION ---
st.title("Welcome to Flexile Llama!")

# User Input for Username
st.sidebar.header("Login")
username = st.sidebar.text_input("Enter your username to continue:", key="username_input")

if username:
    st.sidebar.success(f"Welcome, {username}!")

    # Connect to a user-specific database
    conn = sqlite3.connect(f"{username}_flexile_llama.db")  # Unique database per user
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
    st.markdown("### Track your Fortnite performance over time!")

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

    # Close the connection
    conn.close()

else:
    st.warning("Please enter your username to access Flexile Llama.")
