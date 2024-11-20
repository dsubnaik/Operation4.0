#Program Name: achievements.py
#Developer: Derrick Subnaik
#Date Created: 11/17/2024
# Version: 1.0
#Purpose: Serve the achievements of Operation4.0

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

    # Predefine achievements
    achievements = [
        # Quiz-related achievements
        ("Quiz Novice", "Completed 1 quizzes. Keep up the great work!", "Bronze Quizzer"),
        ("Quiz Intermediate", "Completed 20 quizzes. Impressive dedication!", "Silver Quizzer"),
        ("Quiz Expert", "Completed 50 quizzes. You're a quiz master!", "Gold Quizzer"),
        ("Perfect Score!", "Achieved a perfect score on a quiz.", "A+ Achiever"),

        # Flashcard-related achievements
        ("Flashcard Merchant", "Created 5 flashcards. Kepp it going!", "Flashcard Pro"),
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

    # Insert achievements into the database, avoiding duplicates
    cursor.executemany('''
    INSERT OR IGNORE INTO achievements (name, description, badge)
    VALUES (?, ?, ?)
    ''', achievements)

    conn.commit()
    conn.close()
    print("Achievements tables initialized successfully.")

# Fetch unlocked achievements for a specific user
def get_user_achievements(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT DISTINCT a.name, a.description, a.badge
    FROM achievements a
    JOIN user_achievements ua ON a.id = ua.achievement_id
    WHERE ua.user_id = ?
    ''', (user_id,))

    achievements = cursor.fetchall()
    conn.close()
    return [{'name': row[0], 'description': row[1], 'badge': row[2]} for row in achievements]

# Check and unlock achievements based on user activity
def check_and_unlock_achievement(user_id, action_type, action_count):
    conn = get_connection()
    cursor = conn.cursor()

    # Define criteria for each type of achievement
    achievement_criteria = {
        # Quiz-related achievements
        "quiz_completed": [
            (1, "Quiz Novice"),
            (20, "Quiz Intermediate"),
            (50, "Quiz Expert"),
        ],
        "quiz_perfect_score": [
            (1, "Perfect Score!"),
        ],

        # Flashcard-related achievements
        "flashcard_created": [
            (5, "Flashcard Merchant"),  # Add logic for 5 flashcards
            (10, "Flashcard Creator"),
            (50, "Flashcard Collector"),
            (100, "Flashcard Master"),
        ],
        "flashcard_reviewed": [
            (10, "Flashcard Reviewer"),
        ],

        # Study time achievements
        "study_time_total": [
            (60, "Study Starter"),  # 1 hour
            (600, "Study Pro"),     # 10 hours
            (3000, "Study Guru"),   # 50 hours
        ],

        # Streak achievements
        "study_streak": [
            (2, "One Day Streak"),
            (7, "One Week Streak"),
            (30, "One Month Streak"),
        ],

        # Interaction achievements
        "interaction_shared_tips": [
            (5, "Helpful User"),
        ],
        "interaction_joined_group": [
            (1, "Collaborator"),
        ],
        "interaction_encouraged_others": [
            (10, "Motivator"),
        ],

        # Special achievements
        "quizzes_completed_percentage": [
            (50, "Halfway There"),
            (100, "Ultimate Quizzer"),
        ],
        "flashcards_reviewed_all": [
            (1, "Flashcard Fanatic"),
        ],
        "study_goal_set": [
            (1, "Goal Setter"),
        ],
        "study_goal_achieved": [
            (1, "Goal Achiever"),
        ],
    }

    # Retrieve criteria for the given action type
    criteria = achievement_criteria.get(action_type, [])
    unlocked_achievements = []  # Track newly unlocked achievements
    for count, achievement_name in criteria:
        if action_count >= count:
            # Get the achievement ID
            cursor.execute("SELECT id FROM achievements WHERE name = ?", (achievement_name,))
            achievement_id = cursor.fetchone()
            if achievement_id:
                # Unlock the achievement for the user
                cursor.execute('''
                    INSERT OR IGNORE INTO user_achievements (user_id, achievement_id)
                    VALUES (?, ?)
                ''', (user_id, achievement_id[0]))
                unlocked_achievements.append({
                    "name": achievement_name,
                    "criteria": f"{count} {action_type.replace('_', ' ')}"
                })  # Add to unlocked list with criteria details

    conn.commit()
    conn.close()
    return unlocked_achievements

# Unlock a specific achievement for a user
def unlock_achievement(user_id, achievement_id):
    conn = get_connection()
    cursor = conn.cursor()

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
