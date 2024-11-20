#Program Name: flashcards.py
#Developer: Cassandra Villalobos
#Date Created: 11/17/2024
# Version: 1.0
#Purpose: Includes all methods related to the flashcards
import sqlite3
from datetime import datetime

# Connect to the database
def get_connection():
    return sqlite3.connect('users.db')

# Initialize the flashcards and study_sets tables
def initialize_flashcards_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the flashcards and study_sets tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_set_id INTEGER,
        question TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (study_set_id) REFERENCES study_sets(id)
    )
    ''')
    
    conn.commit()
    conn.close()


# Add a new study set
def add_study_set(user_id, set_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO study_sets (user_id, name) VALUES (?, ?)
        ''', (user_id, set_name))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


# Get all study sets for a user
def get_study_sets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name FROM study_sets WHERE user_id = ?
    ''', (user_id,))
    study_sets = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1]} for row in study_sets]


# Add a flashcard to a specific study set
def add_flashcard(study_set_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO flashcards (study_set_id, question, answer) VALUES (?, ?, ?)
    ''', (study_set_id, question, answer))
    conn.commit()
    conn.close()

# Get all flashcards for a specific study set
def get_flashcards(study_set_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, question, answer FROM flashcards WHERE study_set_id = ?
    ''', (study_set_id,))
    flashcards = cursor.fetchall()
    conn.close()
    
    # Include `id` in each dictionary entry
    return [{'id': row[0], 'question': row[1], 'answer': row[2]} for row in flashcards]


# Delete a study set and all associated flashcards
def delete_study_set(study_set_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM flashcards WHERE study_set_id = ?', (study_set_id,))
    cursor.execute('DELETE FROM study_sets WHERE id = ?', (study_set_id,))
    conn.commit()
    conn.close()

# Delete a specific flashcard from a study set
def delete_flashcard(study_set_id, question):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM flashcards WHERE study_set_id = ? AND question = ?
    ''', (study_set_id, question))
    conn.commit()
    conn.close()

# Update a flashcard within a specific study set
def update_flashcard(study_set_id, old_question, new_question, new_answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE flashcards
    SET question = ?, answer = ?
    WHERE study_set_id = ? AND question = ?
    ''', (new_question, new_answer, study_set_id, old_question))
    conn.commit()
    conn.close()

# Backend: Delete a specific flashcard by ID
def delete_flashcard_from_db(flashcard_id):
    conn = get_connection()
    cursor = conn.cursor()
    print("Deleting flashcard with ID:", flashcard_id)  # Log ID in the database function as well
    cursor.execute('DELETE FROM flashcards WHERE id = ?', (flashcard_id,))
    conn.commit()
    conn.close()

def delete_study_set(study_set_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM flashcards WHERE study_set_id = ?', (study_set_id,))
    cursor.execute('DELETE FROM study_sets WHERE id = ?', (study_set_id,))
    conn.commit()
    conn.close()

