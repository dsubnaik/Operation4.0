import sqlite3

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

    conn.commit()
    conn.close()
    print("Progress tables initialized.")

# Function to add study time for a user
def add_study_time(user_id, hours):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert or update study hours for the user
    cursor.execute('''
    INSERT INTO study_progress (user_id, study_hours)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET study_hours = study_hours + excluded.study_hours
    ''', (user_id, hours))

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

# Function to retrieve a user's progress for display
def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch study hours
    cursor.execute("SELECT study_hours FROM study_progress WHERE user_id = ?", (user_id,))
    study_hours = cursor.fetchone()
    study_hours = study_hours[0] if study_hours else 0

    # Fetch quiz performance
    cursor.execute("SELECT quizzes_passed, total_quizzes FROM quiz_progress WHERE user_id = ?", (user_id,))
    quiz_data = cursor.fetchone()
    quizzes_passed, total_quizzes = quiz_data if quiz_data else (0, 0)

    # Calculate study time percentage (assuming a goal of 10 hours)
    study_time_percentage = min(100, int((study_hours / 10) * 100))
    # Calculate quiz performance percentage
    quiz_performance_percentage = int((quizzes_passed / total_quizzes) * 100) if total_quizzes > 0 else 0

    # Format study time for display
    hours = int(study_hours)
    minutes = int((study_hours - hours) * 60)
    formatted_study_time = f"{hours}h {minutes}m"

    # Return progress data in a structured dictionary
    progress_data = {
        "study_time_percentage": study_time_percentage,
        "study_time": formatted_study_time,
        "quiz_performance_percentage": quiz_performance_percentage,
        "quiz_performance": f"{quizzes_passed}/{total_quizzes}"
    }

    conn.close()
    return progress_data
