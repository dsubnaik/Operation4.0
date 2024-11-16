import sqlite3
import json
from datetime import datetime

# Set the path to your database
DB_PATH = 'C:/Users/derri/OneDrive/Documents/GitHub/Operation4.0/users.db'


def get_connection():
    """Establish a connection to the SQLite database."""
    print(f"Connecting to database at: {DB_PATH}")
    return sqlite3.connect(DB_PATH)


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


def insert_sample_data():
    """Insert sample data into the effort_levels table."""
    conn = get_connection()
    cursor = conn.cursor()

    # Define sample data for user_id 1
    user_id = 1
    week_start_date = datetime.now().strftime('%Y-%m-%d')
    study_frequency = 5
    study_duration_minutes = 600
    focus_areas = json.dumps({"Math": 40, "Science": 30, "History": 30})

    cursor.execute('''
        INSERT INTO effort_levels (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas))

    conn.commit()
    conn.close()
    print("Inserted sample data into 'effort_levels' table.")


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
    insert_sample_data()

    # Verify that data is accessible
    data = get_user_effort_levels(1)
    print(f"Effort data for user_id 1: {data}")
