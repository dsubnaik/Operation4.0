import sqlite3

# Path to the database
DATABASE_PATH = 'users.db'

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def delete_duplicate_entries():
    conn = get_connection()
    cursor = conn.cursor()

    # Delete duplicates while keeping the most recent entry per user
    cursor.execute('''
        DELETE FROM effort_levels
        WHERE id NOT IN (
            SELECT id FROM (
                SELECT id, user_id, MAX(week_start_date)
                FROM effort_levels
                GROUP BY user_id
            )
        )
    ''')

    conn.commit()
    conn.close()
    print("Duplicate entries deleted, only the latest effort level for each user is kept.")

# Run the function to delete duplicates
delete_duplicate_entries()
