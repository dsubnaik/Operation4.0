import sqlite3
import json

DB_PATH = 'C:/Users/derri/OneDrive/Documents/GitHub/Operation4.0/users.db'  # Update if necessary

def get_connection():
    return sqlite3.connect(DB_PATH)

def view_effort_levels(user_id):
    """Retrieve and display effort data for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT week_start_date, study_frequency, study_duration_minutes, focus_areas
        FROM effort_levels
        WHERE user_id = ?
        ORDER BY week_start_date DESC
        LIMIT 1
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        week_start_date, study_frequency, study_duration_minutes, focus_areas_json = result
        focus_areas = json.loads(focus_areas_json) if focus_areas_json else {}
        
        print(f"Effort data for user_id {user_id}:")
        print(f"  Week Start Date: {week_start_date}")
        print(f"  Study Frequency: {study_frequency} days/week")
        print(f"  Study Duration: {study_duration_minutes} minutes")
        print(f"  Focus Areas: {focus_areas}")
    else:
        print(f"No data found for user_id {user_id}.")

# Example usage
if __name__ == "__main__":
    user_id = 1  # Change this ID to view data for different users
    view_effort_levels(user_id)
