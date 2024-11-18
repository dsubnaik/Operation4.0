#Program Name: progress_tracker.py
#Developer: Derrick Subnaik
#Date Created: 11/17/2024
# Version: 1.0
#Purpose: Serve the progress_tracker methods
import sqlite3
from achievements import check_and_unlock_achievement

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Initialize tables to store study and quiz progress
def initialize_progress_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Create study_progress table to track study hours per user
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_progress (
        user_id INTEGER PRIMARY KEY,
        study_hours REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Create quiz_progress table to track quizzes passed and attempted
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_progress (
        user_id INTEGER PRIMARY KEY,
        quizzes_passed INTEGER DEFAULT 0,
        total_quizzes INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Create study_weekly_progress table to track weekly study hours
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_weekly_progress (
        user_id INTEGER,
        week INTEGER,
        study_hours REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, week)
    )
    ''')

    # Create user_performance table to track performance per subject
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_performance (
        user_id INTEGER,
        subject TEXT,
        performance_level REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, subject)
    )
    ''')

    conn.commit()
    conn.close()
    print("Progress tables initialized.")

# Function to add study time for a user (weekly data)
def add_study_time(user_id, week, hours):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert or update study hours for the specific week
    cursor.execute('''
    INSERT INTO study_weekly_progress (user_id, week, study_hours)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, week) DO UPDATE SET study_hours = study_hours + excluded.study_hours
    ''', (user_id, week, hours))

    conn.commit()
    conn.close()

# Function to record quiz results for a user
def record_quiz_result(user_id, passed):
    conn = get_connection()
    cursor = conn.cursor()

    # Increment total quizzes and quizzes passed if the quiz was passed
    cursor.execute('''
    INSERT INTO quiz_progress (user_id, quizzes_passed, total_quizzes)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET 
        quizzes_passed = quizzes_passed + ?,
        total_quizzes = total_quizzes + 1
    ''', (user_id, int(passed), 1, int(passed)))

    conn.commit()
    conn.close()

# Function to update user performance level for a specific subject
def update_user_performance(user_id, subject, performance_level):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert or update performance level for a subject
    cursor.execute('''
    INSERT INTO user_performance (user_id, subject, performance_level)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, subject) DO UPDATE SET performance_level = excluded.performance_level
    ''', (user_id, subject, performance_level))

    conn.commit()
    conn.close()

# Function to retrieve a user's progress for display
def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch weekly study hours
    cursor.execute('''
        SELECT week, study_hours FROM study_weekly_progress
        WHERE user_id = ?
        ORDER BY week
    ''', (user_id,))
    study_hours_data = cursor.fetchall()

    # Prepare weekly study hours
    weeks = [record[0] for record in study_hours_data]
    study_hours = [record[1] for record in study_hours_data]

    # Fetch performance levels per subject
    cursor.execute('''
        SELECT subject, performance_level FROM user_performance
        WHERE user_id = ?
    ''', (user_id,))
    performance_data = cursor.fetchall()

    # Prepare performance levels per subject
    subjects = [record[0] for record in performance_data]
    performance_levels = [record[1] for record in performance_data]

    # Fetch overall study hours and quiz performance
    cursor.execute("SELECT study_hours FROM study_progress WHERE user_id = ?", (user_id,))
    total_study_hours = cursor.fetchone()
    total_study_hours = total_study_hours[0] if total_study_hours else 0

    cursor.execute("SELECT quizzes_passed, total_quizzes FROM quiz_progress WHERE user_id = ?", (user_id,))
    quiz_data = cursor.fetchone()
    quizzes_passed, total_quizzes = quiz_data if quiz_data else (0, 0)

    # Calculate study and quiz performance percentages
    study_time_percentage = min(100, int((total_study_hours / 10) * 100))
    quiz_performance_percentage = int((quizzes_passed / total_quizzes) * 100) if total_quizzes > 0 else 0

    # Format total study time for display
    hours = int(total_study_hours)
    minutes = int((total_study_hours - hours) * 60)
    formatted_study_time = f"{hours}h {minutes}m"

    # Return structured progress data
    progress_data = {
        "study_time_percentage": study_time_percentage,
        "study_time_display": formatted_study_time,
        "quiz_performance_percentage": quiz_performance_percentage,
        "quiz_performance_display": f"{quizzes_passed}/{total_quizzes}",
        "study_hours_weeks": weeks,
        "study_hours": study_hours,
        "subjects": subjects,
        "performance_levels": performance_levels,
    }

    conn.close()
    return progress_data

#method the check if an achievement is unlocked and will store into database
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