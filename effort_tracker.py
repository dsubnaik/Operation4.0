#Program Name: effort_tracker.py
#Developer: Hunter Nichols
#Date Created: 11/17/2024
#Version: 1.0
#Purpose: Serve as te effort tracker of operation 4.0
import sqlite3
import json
from datetime import datetime

# Set the path to your database
DB_PATH = "users.db"

#estable a connection to the database
def get_connection():
    """Establish a connection to the SQLite database."""
    print(f"Connecting to database at: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

#intitialize the effort levels database
def initialize_effort_levels_table():
    """Drop and recreate the effort_levels table."""
    conn = get_connection()
    cursor = conn.cursor()

    # Drop the table if it exists and recreate it
    cursor.execute("DROP TABLE IF EXISTS effort_levels")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS effort_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week_start_date DATE,
            study_frequency INTEGER,
            study_duration_minutes INTEGER,
            focus_areas TEXT,
            UNIQUE(user_id, week_start_date)
        );
    ''')
    conn.commit()
    conn.close()
    print("effort_levels table initialized.")

#get the user effort levels for the user that is logged in
def get_user_effort_levels(user_id):
    """Retrieve the latest effort data for a given user_id."""
    conn = get_connection()
    cursor = conn.cursor()

    # Retrieve the latest week's data for the user
    cursor.execute('''
        SELECT study_frequency, study_duration_minutes, focus_areas
        FROM effort_levels
        WHERE user_id = ?
        ORDER BY week_start_date DESC
        LIMIT 1
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result is None:
        print(f"No data found for user_id {user_id}")
        return None

    study_frequency, study_duration_minutes, focus_areas_json = result
    focus_areas = json.loads(focus_areas_json) if focus_areas_json else {}
    return {
        "study_frequency": study_frequency,
        "study_duration": study_duration_minutes,
        "focus_areas": focus_areas
    }


# Initialize and populate the table if running this script directly
if __name__ == "__main__":
    #initialize_effort_levels_table()
    

    # Verify that data is accessible
    data = get_user_effort_levels(1)
    print(f"Effort data for user_id 1: {data}")
