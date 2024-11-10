import http.server
import socketserver
import urllib
import os
import mimetypes
import json
from authentication import handle_login, handle_signup, fetch_user_details
from achievements import initialize_achievements, get_user_achievements, unlock_achievement
from progress_tracker import initialize_progress_tables, get_user_progress
from effort_tracker import initialize_effort_levels_table, get_user_effort_levels
from userDatabase import initialize_database
from flashcards import initialize_flashcards_table, get_study_sets, get_flashcards, add_study_set, add_flashcard
from resource_handler import initialize_resources_table, get_resources, generate_resources_html


PORT = 8000
TEMPLATES_DIR = 'templates'
CSS_DIR = 'css'

# Session dictionary to manage user sessions based on IP address
sessions = {}

# Function to serve HTML pages or static files (e.g., CSS)
def serve_page(handler, file_path, content_type='text/html'):
    try:
        with open(file_path, 'rb') as file:
            handler.send_response(200)
            handler.send_header('Content-type', content_type)
            handler.end_headers()
            handler.wfile.write(file.read())
    except FileNotFoundError:
        handler.send_response(404)
        handler.end_headers()
        handler.wfile.write(b'Page not found')

# API endpoint to fetch study sets
def get_study_sets_for_user(handler, user_id):
    study_sets = get_study_sets(user_id)
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(study_sets).encode("utf-8"))

# API endpoint to fetch flashcards for a study set
def get_flashcards_for_study_set(handler, study_set_id):
    flashcards = get_flashcards(study_set_id)
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(flashcards).encode("utf-8"))

# Helper function to parse JSON POST data
def parse_json_post_data(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return json.loads(post_data.decode('utf-8'))

class CustomHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/splashpage.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "splashpage.html"))
        elif self.path == "/home.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "home.html"))
        elif self.path == "/login_screen.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "login_screen.html"))
        elif self.path == "/flashcards.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "flashcards.html"))
        elif self.path == "/quiz.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "quiz.html"))
        elif self.path == "/account.html":
            if self.client_address[0] in sessions:
                user_data = sessions[self.client_address[0]]
                self.serve_account_page(user_data)
            else:
                redirect(self, '/login_screen.html')
        elif self.path == "/achievements.html":
            if self.client_address[0] in sessions:
                user_data = sessions[self.client_address[0]]
                self.serve_achievements_page(user_data['id'])
            else:
                redirect(self, '/login_screen.html')
        elif self.path == "/progress.html":
            if self.client_address[0] in sessions:
                user_data = sessions[self.client_address[0]]
                self.serve_progress_page(user_data['id'])
            else:
                redirect(self, '/login_screen.html')
        elif self.path == "/effort-levels.html":
            if self.client_address[0] in sessions:
                user_data = sessions[self.client_address[0]]
                self.serve_effort_levels_page(user_data['id'])
            else:
                redirect(self, '/login_screen.html')
        elif self.path == "/recommended-sources.html":
            if self.client_address[0] in sessions:
                user_data = sessions[self.client_address[0]]
                self.serve_recommended_resources_page(user_data['id'])
            else:
                redirect(self, '/login_screen.html')
        elif self.path == "/signup.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "signup.html"))
        elif self.path == "/study.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "study.html"))
        elif self.path == "/logout":
            if self.client_address[0] in sessions:
                del sessions[self.client_address[0]]
            redirect(self, '/login_screen.html')
        elif self.path.startswith("/css/"):
            file_path = os.path.join(CSS_DIR, self.path[5:])
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'text/css'
            serve_page(self, file_path, content_type)
        elif self.path == "/api/get_study_sets":
            user_ip = self.client_address[0]
            user_data = sessions.get(user_ip)
            if user_data:
                user_id = user_data.get("id")
                get_study_sets_for_user(self, user_id)
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized"}')

        elif self.path.startswith("/api/get_flashcards"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            study_set_id = params.get("study_set_id", [None])[0]
            if study_set_id:
                get_flashcards_for_study_set(self, int(study_set_id))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Study set ID required"}')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/add_study_set':
            data = parse_json_post_data(self)
            set_name = data.get('set_name')
            user_id = sessions.get(self.client_address[0], {}).get("id")
            if user_id and set_name:
                new_set_id = add_study_set(user_id, set_name)
                if new_set_id:
                    self.send_response(201)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"id": new_set_id, "name": set_name}).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error": "Study set with that name already exists."}')
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized or missing data"}')

        elif self.path == '/api/add_flashcard':
            data = parse_json_post_data(self)
            study_set_id = data.get('study_set_id')
            question = data.get('question')
            answer = data.get('answer')
            if study_set_id and question and answer:
                add_flashcard(study_set_id, question, answer)
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"message": "Flashcard added successfully"}')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing study set ID, question, or answer"}')

        elif self.path == '/login_screen.html':
            post_data = parse_post_data(self)
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            user_data = handle_login(username, password)
            if user_data:
                sessions[self.client_address[0]] = user_data
                redirect(self, '/home.html')
            else:
                redirect(self, '/login_screen.html?error=1')

        elif self.path == '/signup.html':
            post_data = parse_post_data(self)
            first_name = post_data.get('first_name', [''])[0]
            last_name = post_data.get('last_name', [''])[0]
            email = post_data.get('email', [''])[0]
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            confirm_password = post_data.get('confirm_password', [''])[0]

            if password != confirm_password:
                redirect(self, '/signup.html?error=password_mismatch')
                return

            if handle_signup(username, password, first_name, last_name, email):
                redirect(self, '/home.html')
            else:
                redirect(self, '/signup.html?error=user_exists')

    def serve_account_page(self, user_data):
        user_info = fetch_user_details(user_data["username"])
        with open(os.path.join(TEMPLATES_DIR, "account.html"), 'r', encoding='utf-8') as file:
            html_content = file.read()
            html_content = html_content.replace("John Doe", f"{user_info['first_name']} {user_info['last_name']}")
            html_content = html_content.replace("johndoe@example.com", user_info['email'])

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def serve_achievements_page(self, user_id):
        # Fetch unlocked achievements for the user
        unlocked_achievements = get_user_achievements(user_id)
        
        # Debug print statement to check retrieved achievements
        print("Retrieved achievements:", unlocked_achievements)
        
        achievements_html = "".join(
            f"<div class='achievement-card'><h3>{name}</h3><p>{description}</p><div class='achievement-badge'>{badge}</div></div>"
            for name, description, badge in unlocked_achievements
        )

        with open(os.path.join(TEMPLATES_DIR, "achievements.html"), "r", encoding="utf-8") as file:
            html_content = file.read().replace("<!-- ACHIEVEMENTS_PLACEHOLDER -->", achievements_html)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


    def serve_progress_page(self, user_id):
        # Fetch progress data for the user
        progress_data = get_user_progress(user_id)

        # Ensure values are formatted as expected
        study_time_display = progress_data.get('study_time', 'No data recorded')
        study_time_percentage = f"{progress_data.get('study_time_percentage', 0)}%"
        quiz_performance_display = progress_data.get('quiz_performance', 'No quizzes taken')
        quiz_performance_percentage = f"{progress_data.get('quiz_performance_percentage', 0)}%"

        # Load HTML template and replace placeholders with dynamic data
        with open(os.path.join(TEMPLATES_DIR, "progress.html"), "r", encoding="utf-8") as file:
            html_content = file.read()
            html_content = html_content.replace("{{STUDY_TIME_PERCENTAGE}}", study_time_percentage)
            html_content = html_content.replace("{{STUDY_TIME_DISPLAY}}", study_time_display)
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_PERCENTAGE}}", quiz_performance_percentage)
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_DISPLAY}}", quiz_performance_display)

        # Send response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


    def serve_effort_levels_page(self, user_id):
        effort_data = get_user_effort_levels(user_id)
        study_frequency = f"{effort_data['study_frequency']} days/week" if effort_data else "No data recorded yet"
        study_duration = f"{divmod(effort_data['study_duration'], 60)}" if effort_data else "No data recorded yet"
        focus_areas_html = "<ul>" + "".join(
            f"<li><span>{subject}</span> - {percentage}% of study time</li>"
            for subject, percentage in effort_data['focus_areas'].items()
        ) + "</ul>" if effort_data else "<li>No data recorded yet</li>"

        with open(os.path.join(TEMPLATES_DIR, "effort-levels.html"), "r", encoding="utf-8") as file:
            html_content = file.read().replace("60%", study_frequency).replace("7h 30m", study_duration).replace("<ul></ul>", focus_areas_html)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_recommended_resources_page(self, user_id):
        resources_html = generate_resources_html()

        with open(os.path.join(TEMPLATES_DIR, "recommended-sources.html"), "r", encoding="utf-8") as file:
            html_content = file.read().replace("<!-- RESOURCES_PLACEHOLDER -->", resources_html)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


# Helper functions
def parse_post_data(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return urllib.parse.parse_qs(post_data.decode('utf-8'))

def redirect(handler, location):
    handler.send_response(302)
    handler.send_header('Location', location)
    handler.end_headers()

# Initialize all required database tables on server startup
initialize_database()
initialize_achievements()
initialize_progress_tables()
initialize_effort_levels_table()
initialize_resources_table()
initialize_flashcards_table()

# Start the HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
