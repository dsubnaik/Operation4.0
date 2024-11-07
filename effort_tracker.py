import sqlite3
import json
from datetime import datetime, timedelta

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Initialize the effort_levels table
def initialize_effort_levels_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the effort_levels table if it doesn't exist, with a unique constraint on user_id and week_start_date
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS effort_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week_start_date DATE,
        study_frequency INTEGER,
        study_duration_minutes INTEGER,
        focus_areas TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, week_start_date)  -- Ensures one entry per user per week
    )
    ''')
    
    conn.commit()
    conn.close()

# Insert or update effort data for a specific week
def update_effort_levels(user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert focus areas dictionary to JSON format for storage
    focus_areas_json = json.dumps(focus_areas)
    
    # Attempt to insert; if conflict, update the row instead
    cursor.execute('''
    INSERT INTO effort_levels (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(user_id, week_start_date) 
    DO UPDATE SET 
        study_frequency=excluded.study_frequency, 
        study_duration_minutes=excluded.study_duration_minutes, 
        focus_areas=excluded.focus_areas
    ''', (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas_json))
    
    conn.commit()
    conn.close()

# Fetch the latest effort data for a user
def get_user_effort_levels(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get the most recent effort data
    cursor.execute('''
    SELECT study_frequency, study_duration_minutes, focus_areas
    FROM effort_levels
    WHERE user_id = ?
    ORDER BY week_start_date DESC
    LIMIT 1
    ''', (user_id,))
    
    effort_data = cursor.fetchone()
    conn.close()
    
    # Return the effort data as a dictionary
    if effort_data:
        # Convert JSON string back to dictionary for focus areas
        focus_areas = json.loads(effort_data[2])
        return {
            "study_frequency": effort_data[0],
            "study_duration": effort_data[1],
            "focus_areas": focus_areas
        }
    else:
        return None
