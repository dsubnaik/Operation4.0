import sqlite3

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Initialize achievements and user_achievements tables
def initialize_achievements():
    conn = get_connection()
    cursor = conn.cursor()

    # Create achievements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        badge TEXT
    )
    ''')

    # Create user_achievements table with a unique constraint to prevent duplicates
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_id INTEGER,
        unlock_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (achievement_id) REFERENCES achievements(id),
        UNIQUE (user_id, achievement_id)  -- Prevent duplicate achievements for the same user
    )
    ''')

    # Populate achievements table with default achievements if not already present
    achievements = [
        ("First Quiz Completed", "Congratulations on completing your first quiz!", "Beginner Level"),
        ("First Flashcard Created", "You've created your first flashcard.", "Flashcard Novice"),
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO achievements (name, description, badge)
    VALUES (?, ?, ?)
    ''', achievements)

    conn.commit()
    conn.close()
    print("Achievements tables initialized.")

# Fetch unlocked achievements for a specific user
def get_user_achievements(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT a.name, a.description, a.badge
    FROM achievements a
    JOIN user_achievements ua ON a.id = ua.achievement_id
    WHERE ua.user_id = ?
    """, (user_id,))

    achievements = cursor.fetchall()
    conn.close()
    return achievements


# Check and unlock an achievement for a user
def unlock_achievement(user_id, achievement_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Use INSERT OR IGNORE to avoid duplicates
    cursor.execute('''
    INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
    VALUES (?, ?)
    ''', (user_id, achievement_id))

    conn.commit()
    conn.close()
    print(f"Achievement {achievement_id} unlocked for user {user_id}.")
    
# Cleanup duplicates in user_achievements table
def clean_up_duplicates():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete duplicate entries while keeping the earliest unlock date for each user/achievement pair
    cursor.execute('''
    DELETE FROM user_achievements
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM user_achievements
        GROUP BY user_id, achievement_id
    )
    ''')

    conn.commit()
    conn.close()
    print("Duplicate entries removed from user_achievements table.")
