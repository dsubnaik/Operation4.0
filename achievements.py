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

    achievements = [
        # Quiz-related achievements
        ("Quiz Novice", "Completed 5 quizzes. Keep up the great work!", "Bronze Quizzer"),
        ("Quiz Intermediate", "Completed 20 quizzes. Impressive dedication!", "Silver Quizzer"),
        ("Quiz Expert", "Completed 50 quizzes. You're a quiz master!", "Gold Quizzer"),
        ("Perfect Score!", "Achieved a perfect score on a quiz.", "A+ Achiever"),

        # Flashcard-related achievements
        ("Flashcard Creator", "Created 10 flashcards. Great start!", "Flashcard Apprentice"),
        ("Flashcard Collector", "Created 50 flashcards. Building a great collection!", "Flashcard Enthusiast"),
        ("Flashcard Master", "Created 100 flashcards. You're a flashcard expert!", "Flashcard Mastery"),
        ("Flashcard Reviewer", "Reviewed flashcards 10 times. Keep revisiting to retain knowledge!", "Review Beginner"),
        
        # Study time achievements
        ("Study Starter", "Spent 1 hour studying in total.", "Time Investor"),
        ("Study Pro", "Spent 10 hours studying in total.", "Dedicated Scholar"),
        ("Study Guru", "Spent 50 hours studying in total.", "Study Guru"),

        # Streak achievements
        ("One Day Streak", "Studied for two consecutive days. Keep it up!", "Streak Starter"),
        ("One Week Streak", "Studied for seven consecutive days. Consistency is key!", "Streak Enthusiast"),
        ("One Month Streak", "Studied for 30 consecutive days. Amazing dedication!", "Streak Champion"),

        # Interaction achievements
        ("Helpful User", "Shared tips with others 5 times.", "Community Helper"),
        ("Collaborator", "Joined a study group.", "Team Player"),
        ("Motivator", "Encouraged others 10 times in discussions.", "Positive Influence"),

        # Special achievements
        ("Halfway There", "Completed 50% of all available quizzes.", "Milestone Achiever"),
        ("Ultimate Quizzer", "Completed all available quizzes.", "Quiz Conqueror"),
        ("Flashcard Fanatic", "Reviewed every flashcard created.", "Flashcard Fanatic"),
        ("Goal Setter", "Set a study goal for the first time.", "Goal-Oriented"),
        ("Goal Achiever", "Achieved a set study goal.", "Goal Getter"),
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

def check_and_unlock_achievement(user_id, action_type, action_count):
    conn = get_connection()
    cursor = conn.cursor()

    achievement_criteria = {
        "quiz_completed": [
            (5, "Quiz Novice"),
            (20, "Quiz Intermediate"),
            (50, "Quiz Expert")
        ],
        "flashcard_created": [
            (10, "Flashcard Creator"),
            (50, "Flashcard Collector"),
            (100, "Flashcard Master")
        ],
        # Add other criteria here
    }

    criteria = achievement_criteria.get(action_type, [])
    for count, achievement_name in criteria:
        if action_count >= count:
            cursor.execute("SELECT id FROM achievements WHERE name = ?", (achievement_name,))
            achievement_id = cursor.fetchone()
            if achievement_id:
                unlock_achievement(user_id, achievement_id[0])  # Unlock the achievement

    conn.close()

def unlock_achievement(user_id, achievement_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
    VALUES (?, ?)
    ''', (user_id, achievement_id))

    conn.commit()
    conn.close()