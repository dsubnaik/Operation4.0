import sqlite3
import json

# Path to the database
DATABASE_PATH = 'users.db'

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def view_study_progress():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Study Progress Data:")
    print("User ID | Study Hours")
    print("---------------------")
    cursor.execute("SELECT user_id, study_hours FROM study_progress")
    for row in cursor.fetchall():
        print(f"{row[0]:<8} | {row[1]}")
    
    conn.close()
    print()

def view_quiz_progress():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Quiz Progress Data:")
    print("User ID | Quizzes Passed | Total Quizzes")
    print("----------------------------------------")
    cursor.execute("SELECT user_id, quizzes_passed, total_quizzes FROM quiz_progress")
    for row in cursor.fetchall():
        print(f"{row[0]:<8} | {row[1]:<15} | {row[2]}")
    
    conn.close()
    print()

def view_effort_levels():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Effort Levels Data:")
    print("User ID | Week Start Date | Study Frequency | Study Duration (mins) | Focus Areas")
    print("-------------------------------------------------------------------------")
    cursor.execute("SELECT user_id, week_start_date, study_frequency, study_duration_minutes, focus_areas FROM effort_levels")
    for row in cursor.fetchall():
        user_id, week_start_date, study_frequency, study_duration, focus_areas = row
        
        # Try to decode focus_areas JSON data; handle malformed data gracefully
        try:
            focus_areas_dict = json.loads(focus_areas)
        except (json.JSONDecodeError, TypeError):
            focus_areas_dict = "Invalid data"  # Display "Invalid data" if JSON decoding fails
        
        print(f"{user_id:<8} | {week_start_date} | {study_frequency:<15} | {study_duration:<20} | {focus_areas_dict}")
    
    conn.close()
    print()

# Execute the view functions
view_study_progress()
view_quiz_progress()
view_effort_levels()
