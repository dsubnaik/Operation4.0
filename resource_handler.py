# resource_handler.py

import sqlite3
import os

DATABASE_PATH = 'users.db'

# Initialize resources table
def initialize_resources_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        link TEXT NOT NULL,
        resource_type TEXT,
        subject TEXT
    )
    ''')

    # Sample resources
    resources = [
        ("Understanding Algebra Basics", "This article covers algebra basics.", "https://example.com/algebra-basics", "Article", "Math"),
        ("The Scientific Method Explained", "Short video on the scientific method.", "https://example.com/scientific-method-video", "Video", "Science"),
        ("World History: Key Events Timeline", "Timeline of significant events in history.", "https://example.com/history-timeline", "External Link", "History"),
        ("Introduction to English Literature", "E-book covering key themes in literature.", "https://example.com/english-literature-ebook", "E-book", "English")
    ]
    
    # Insert sample resources
    cursor.executemany('''
    INSERT OR IGNORE INTO resources (title, description, link, resource_type, subject)
    VALUES (?, ?, ?, ?, ?)
    ''', resources)

    conn.commit()
    conn.close()

# Fetch all resources from the database
def get_resources():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT title, description, link, resource_type, subject FROM resources")
    resources = cursor.fetchall()
    
    conn.close()
    
    return [
        {"title": title, "description": description, "link": link, "type": resource_type, "subject": subject}
        for title, description, link, resource_type, subject in resources
    ]

# Generate HTML for resources
def generate_resources_html():
    resources = get_resources()
    resources_html = ""

    for resource in resources:
        resources_html += f"""
        <div class="resource-card">
            <span class="resource-type">{resource['type']}</span>
            <h3>{resource['title']}</h3>
            <p>{resource['description']}</p>
            <p><a href="{resource['link']}" target="_blank">Visit resource</a></p>
            <span class="subject-badge">{resource['subject']}</span>
        </div>
        """
    return resources_html
