import sqlite3

# Function to get a connection to the database
def get_connection():
    return sqlite3.connect('users.db')

# Function to initialize the database
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        email TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("User database initialized.")
