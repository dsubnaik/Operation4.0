import sqlite3

def handle_login(username, password):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the user exists with the provided username and password
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()

    # Return True if a user is found, otherwise False
    return user is not None

def handle_signup(username, password, first_name, last_name, email):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Insert the new user into the users table
        cursor.execute('INSERT INTO users (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)', 
                       (username, password, first_name, last_name, email))
        conn.commit()
    except sqlite3.IntegrityError:
        # Username already exists, return False
        conn.close()
        return False

    conn.close()

    # Return True if signup is successful
    return True
