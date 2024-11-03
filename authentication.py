import sqlite3

def handle_login(username, password):
    """
    Attempt to log in a user by verifying their username and password.
    Returns the user's details if successful, or None if login fails.
    """
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the user exists with the provided username and password
    cursor.execute('SELECT id, username, first_name, last_name, email FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()

    # Return user details as a dictionary if found, otherwise None
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "first_name": user[2],
            "last_name": user[3],
            "email": user[4]
        }
    return None

def handle_signup(username, password, first_name, last_name, email):
    """
    Registers a new user in the system.
    Returns True if the signup is successful, or False if the username already exists.
    """
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Insert the new user into the users table
        cursor.execute(
            'INSERT INTO users (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)',
            (username, password, first_name, last_name, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Username already exists, return False
        conn.close()
        return False

    conn.close()
    return True

def fetch_user_details(username):
    """
    Retrieves detailed information about a user based on their username.
    Returns a dictionary with user details if found, otherwise None.
    """
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Query user details by username
    cursor.execute('SELECT first_name, last_name, email FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "first_name": user[0],
            "last_name": user[1],
            "email": user[2]
        }
    return None
