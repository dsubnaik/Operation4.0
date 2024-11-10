import sqlite3

# Path to your database file (adjust if it's in a different location)
DATABASE_PATH = 'users.db'

def fetch_study_sets():
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Query to fetch all study sets; adjust the table name and columns if needed
        cursor.execute('SELECT id, name FROM study_sets')
        study_sets = cursor.fetchall()

        if study_sets:
            print("Study Sets:")
            for set_id, set_name in study_sets:
                print(f"ID: {set_id}, Name: {set_name}")
        else:
            print("No study sets found in the database.")

    except sqlite3.Error as e:
        print("Error accessing the database:", e)

    finally:
        # Close the database connection
        conn.close()

# Run the script to fetch and display study sets
if __name__ == "__main__":
    fetch_study_sets()
