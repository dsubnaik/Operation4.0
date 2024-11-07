import sqlite3
import json
import random

# Path to the database
DATABASE_PATH = 'users.db'

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def update_zero_focus_areas():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch entries where all focus area values are zero
    cursor.execute('''
        SELECT id, focus_areas
        FROM effort_levels
        WHERE focus_areas = '{"Math": 0, "Science": 0, "History": 0}'
    ''')
    
    zero_entries = cursor.fetchall()

    # Update each zero-entry with random values
    for entry_id, focus_areas_json in zero_entries:
        # Generate random non-zero values for each subject
        updated_focus_areas = {
            "Math": random.randint(10, 50),
            "Science": random.randint(10, 50),
            "History": random.randint(10, 50)
        }
        
        # Convert updated dictionary to JSON format for storage
        updated_focus_areas_json = json.dumps(updated_focus_areas)
        
        # Update the entry in the database
        cursor.execute('''
            UPDATE effort_levels
            SET focus_areas = ?
            WHERE id = ?
        ''', (updated_focus_areas_json, entry_id))
    
    conn.commit()
    conn.close()
    print("Zero entries updated with random focus area values.")

# Run the function to update entries
update_zero_focus_areas()
