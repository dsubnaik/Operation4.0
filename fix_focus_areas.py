import sqlite3
import json

# Path to the database
DATABASE_PATH = 'users.db'

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def fix_invalid_focus_areas():
    """Update the focus_areas column with valid JSON where entries are invalid."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Retrieve all rows in the effort_levels table
    cursor.execute("SELECT id, focus_areas FROM effort_levels")
    rows = cursor.fetchall()

    for row in rows:
        entry_id, focus_areas = row

        try:
            # Try to parse focus_areas as JSON
            json.loads(focus_areas)
        except (json.JSONDecodeError, TypeError):
            # If focus_areas is invalid JSON, replace it with a default valid JSON structure
            default_focus_areas = json.dumps({"Math": 0, "Science": 0, "History": 0})
            cursor.execute("UPDATE effort_levels SET focus_areas = ? WHERE id = ?", (default_focus_areas, entry_id))
            print(f"Updated entry ID {entry_id} with default focus_areas JSON.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Focus areas data has been fixed.")

# Run the function to fix invalid focus_areas data
fix_invalid_focus_areas()
