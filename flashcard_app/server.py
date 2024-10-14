import http.server
import socketserver
import urllib.parse
import sqlite3
import json

PORT = 8000

# Initialize the database (creates tables for users and flashcards if they don't exist)
def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create a users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create a flashcards table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        user_id INTEGER
    )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables initialized.")

# Function to check login credentials
def check_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to add a new user (for registration)
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

# Function to add a new flashcard
def add_flashcard(question, answer, user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO flashcards (question, answer, user_id) VALUES (?, ?, ?)', (question, answer, user_id))
    conn.commit()
    conn.close()

# Function to retrieve all flashcards
def get_flashcards():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flashcards')
    flashcards = cursor.fetchall()
    conn.close()
    return flashcards

# HTTP request handler
class CustomHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        # Handle login form submission
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            username = post_data['username'][0]
            password = post_data['password'][0]

            if check_login(username, password):
                self.send_response(302)
                self.send_header('Location', '/home.html')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login_screen.html?error=1')
                self.end_headers()

        # Handle registration form submission
        elif self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            username = post_data['username'][0]
            password = post_data['password'][0]

            if add_user(username, password):
                self.send_response(302)
                self.send_header('Location', '/login_screen.html?success=1')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/register.html?error=1')  # Redirect to register page on failure
                self.end_headers()

        # Handle adding a flashcard
        elif self.path == '/add_flashcard':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            flashcard_data = json.loads(post_data.decode('utf-8'))

            question = flashcard_data['question']
            answer = flashcard_data['answer']
            user_id = flashcard_data.get('user_id', None)

            add_flashcard(question, answer, user_id)

            self.send_response(200)
            self.end_headers()

    def do_GET(self):
        # Handle fetching flashcards
        if self.path == '/flashcards':
            flashcards = get_flashcards()

            # Send back the flashcards as JSON
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([{
                'question': flashcard[1],  # Assuming 1 is the question column in DB
                'answer': flashcard[2]    # Assuming 2 is the answer column in DB
            } for flashcard in flashcards]).encode('utf-8'))
        else:
            # For static files (HTML, CSS, JS), serve as normal
            super().do_GET()

# Initialize the database
initialize_database()

# Start the HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
