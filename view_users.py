import sqlite3
import os

def view_users(database_path='users.db'):
    # Ensure the database file exists
    if not os.path.exists(database_path):
        print(f"Database file '{database_path}' not found.")
        return

    # Connect to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Check if the 'users' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("The 'users' table does not exist in the database.")
        conn.close()
        return

    # Fetch and display user data
    try:
        cursor.execute("SELECT id, username, first_name, last_name, email FROM users")
        users = cursor.fetchall()

        # Display user information
        if users:
            print("Current users in the database:")
            print("{:<5} {:<15} {:<15} {:<15} {:<25}".format("ID", "Username", "First Name", "Last Name", "Email"))
            print("-" * 75)
            for user in users:
                print("{:<5} {:<15} {:<15} {:<15} {:<25}".format(user[0], user[1], user[2], user[3], user[4]))
        else:
            print("No users found in the database.")

    except sqlite3.Error as e:
        print("Error accessing the database:", e)

    # Close the database connection
    conn.close()

# Run the function to view users
view_users('users.db')
