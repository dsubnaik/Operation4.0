#Program Name: authentication.py
#Developer: Daniel Carlos, Angela Franco
#Date Created: 11/17/2024
#Version: 1.0
#Purpose: Serve the authentication of Operation4.0 such as LogIn and SignUp features.
import sqlite3

#This will handle the the log in for each user
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

#this will handle the sign up for each user
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

#method to get the user information from the databas
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


def update_user_info(user_id, username, name, new_password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        if username:
            print(f"Updating username to {username} for user ID {user_id}")
            cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
        
        if name:
            print(f"Updating name to {name} for user ID {user_id}")
            first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
            cursor.execute('UPDATE users SET first_name = ?, last_name = ? WHERE id = ?', (first_name, last_name, user_id))
        
        if new_password:
            print(f"Updating password for user ID {user_id}")
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        
        # Removed email_notifications update

        conn.commit()
        print("User information updated successfully in the database.")
        return True
    except sqlite3.Error as e:
        print("Database error:", e)
        conn.rollback()
        return False
    finally:
        conn.close()
