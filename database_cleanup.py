import sqlite3

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Drop the existing user_achievements table and recreate with UNIQUE constraint if needed
def recreate_user_achievements_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Rename existing table for backup
    cursor.execute("ALTER TABLE user_achievements RENAME TO user_achievements_old;")
    
    # Recreate table with UNIQUE constraint
    cursor.execute('''
    CREATE TABLE user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_id INTEGER,
        unlock_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (achievement_id) REFERENCES achievements(id),
        UNIQUE (user_id, achievement_id)
    );
    ''')
    
    # Copy data back into new table (ignoring duplicates)
    cursor.execute('''
    INSERT OR IGNORE INTO user_achievements (user_id, achievement_id, unlock_date)
    SELECT user_id, achievement_id, unlock_date FROM user_achievements_old;
    ''')
    
    # Drop the old table
    cursor.execute("DROP TABLE user_achievements_old;")
    
    conn.commit()
    conn.close()
    print("Recreated user_achievements table with UNIQUE constraint.")

# Run the function to recreate the table if needed
if __name__ == "__main__":
    recreate_user_achievements_table()
