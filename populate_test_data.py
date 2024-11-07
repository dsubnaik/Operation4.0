import sqlite3
import random
from datetime import datetime, timedelta
import json

# Path to the database
DATABASE_PATH = 'users.db'

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

# Sample user IDs (assuming they are integers from 1 to 14)
user_ids = list(range(1, 15))

def populate_effort_levels():
    """Populate the effort_levels table with realistic data for each user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    for user_id in user_ids:
        # Random weekly study frequency (1 to 7 days) and duration (60 to 600 minutes)
        study_frequency = random.randint(1, 7)
        study_duration = random.randint(60, 600)
        
        # Random distribution of focus areas that sum up to around 100%
        math_focus = random.randint(10, 50)
        science_focus = random.randint(10, 50)
        history_focus = max(0, 100 - (math_focus + science_focus))  # Ensure total is around 100%
        
        # Format focus_areas as JSON
        focus_areas = {
            "Math": math_focus,
            "Science": science_focus,
            "History": history_focus
        }
        focus_areas_json = json.dumps(focus_areas)
        
        # Randomize week_start_date within the past 30 days
        week_start_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        
        # Insert or replace data in the effort_levels table
        cursor.execute('''
            INSERT OR REPLACE INTO effort_levels (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, week_start_date, study_frequency, study_duration, focus_areas_json))
    
    conn.commit()
    conn.close()
    print("Effort levels data populated with varied focus areas.")

# Run the function to populate the effort levels with more realistic data
populate_effort_levels()
