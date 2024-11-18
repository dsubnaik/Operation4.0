#Program Name: server.py
#Developer: Hunter Nichils
#Date Created: 11/17/2024
# Version: 1.0
#Purpose: The ability to store time tracked with certain pages within the application
from datetime import datetime
import json
import sqlite3

def get_connection():
    return sqlite3.connect("users.db")

def initialize_time_tracking_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_time_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            page TEXT NOT NULL,
            time_spent INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    print("Time tracking table initialized.")

def handle_page_time_tracking(handler, sessions):
    try:
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        user_ip = handler.client_address[0]
        user_data = sessions.get(user_ip)
        if not user_data:
            handler.send_response(403)
            handler.end_headers()
            handler.wfile.write(b'{"error": "Unauthorized"}')
            return

        user_id = user_data["id"]
        page = data.get("page")
        time_spent = data.get("time_spent")

        if not page or time_spent is None:
            handler.send_response(400)
            handler.end_headers()
            handler.wfile.write(b'{"error": "Invalid data"}')
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO page_time_tracking (user_id, page, time_spent)
            VALUES (?, ?, ?)
        ''', (user_id, page, time_spent))
        conn.commit()
        conn.close()

        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(b'{"message": "Time tracked successfully"}')

    except Exception as e:
        print(f"Error handling page time tracking: {e}")
        handler.send_response(500)
        handler.end_headers()
        handler.wfile.write(b'{"error": "Internal server error"}')
