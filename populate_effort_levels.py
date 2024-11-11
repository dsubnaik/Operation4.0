import sqlite3
import json
from datetime import datetime
import random

DB_PATH = 'C:/Users/derri/OneDrive/Documents/GitHub/Operation4.0/users.db'  # Update if necessary

def get_connection():
    return sqlite3.connect(DB_PATH)

def populate_effort_levels_for_all_users():
    """Populate effort data with random values for all users."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get all user IDs from the users table
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    week_start_date = datetime.now().strftime('%Y-%m-%d')

    for user_id in user_ids:
        # Generate random data for each user
        study_frequency = random.randint(1, 7)  # Random study frequency between 1 and 7 days per week
        study_duration_minutes = random.randint(120, 1000)  # Random study duration between 2 hours and ~16 hours

        # Generate random focus areas with percentages that add up to 100%
        focus_areas = {
            "Math": random.randint(10, 50),
            "Science": random.randint(10, 50),
            "History": random.randint(10, 50)
        }
        # Adjust focus areas to make sure percentages sum to 100
        total_percentage = sum(focus_areas.values())
        focus_areas = {k: int(v * 100 / total_percentage) for k, v in focus_areas.items()}

        # Convert focus areas to JSON
        focus_areas_json = json.dumps(focus_areas)

        # Insert or update the record for the user
        cursor.execute('''
            INSERT INTO effort_levels (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, week_start_date) 
            DO UPDATE SET 
                study_frequency=excluded.study_frequency, 
                study_duration_minutes=excluded.study_duration_minutes, 
                focus_areas=excluded.focus_areas
        ''', (user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas_json))
        
        print(f"Random data populated for user_id {user_id}.")

    conn.commit()
    conn.close()
    print("Effort levels populated with random data for all users.")

# Run the script
if __name__ == "__main__":
    populate_effort_levels_for_all_users()
