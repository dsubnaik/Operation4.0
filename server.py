import http.server
import socketserver
from authentication import handle_login, handle_signup, fetch_user_details
from achievements import initialize_achievements, get_user_achievements
from progress_tracker import initialize_progress_tables, get_user_progress
from effort_tracker import initialize_effort_levels_table, get_user_effort_levels
from resource_handler import initialize_resources_table, get_resources
from userDatabase import initialize_database
import urllib
import os
import mimetypes

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
        else:
            super().do_GET()

    def do_POST(self):
        post_data = parse_post_data(self)

        if self.path == '/login_screen.html':
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            user_data = handle_login(username, password)
            if user_data:
                sessions[self.client_address[0]] = user_data
                redirect(self, '/home.html')
            else:
                redirect(self, '/login_screen.html?error=1')

        elif self.path == '/signup.html':
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
        unlocked_achievements = get_user_achievements(user_id)

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
        progress_data = get_user_progress(user_id)

        # Extract values or set default messages
        study_time_display = progress_data.get('study_time', 'No data recorded')
        study_time_percentage = f"{progress_data.get('study_time_percentage', 0)}%"
        quiz_performance_display = progress_data.get('quiz_performance', 'No quizzes taken')
        quiz_performance_percentage = f"{progress_data.get('quiz_performance_percentage', 0)}%"

        with open(os.path.join(TEMPLATES_DIR, "progress.html"), "r", encoding="utf-8") as file:
            html_content = file.read()
            html_content = html_content.replace("{{STUDY_TIME_PERCENTAGE}}", study_time_percentage)
            html_content = html_content.replace("{{STUDY_TIME_DISPLAY}}", study_time_display)
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_PERCENTAGE}}", quiz_performance_percentage)
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_DISPLAY}}", quiz_performance_display)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_effort_levels_page(self, user_id):
        effort_data = get_user_effort_levels(user_id)

        if not effort_data:
            study_frequency = "No data recorded yet"
            study_duration = "No data recorded yet"
            focus_areas_html = "<li>No data recorded yet</li>"
            study_frequency_percentage = "0%"
            study_duration_percentage = "0%"
        else:
            study_frequency = f"{effort_data['study_frequency']} days/week"
            hours, minutes = divmod(effort_data['study_duration'], 60)
            study_duration = f"{hours}h {minutes}m"
            focus_areas_html = "".join(
                f"<li><span>{subject}</span> - {percentage}% of study time</li>"
                for subject, percentage in effort_data['focus_areas'].items()
            )
            study_frequency_percentage = f"{effort_data['study_frequency'] * 10}%"
            study_duration_percentage = f"{min(effort_data['study_duration'] / 10, 100)}%"

        with open(os.path.join(TEMPLATES_DIR, "effort-levels.html"), "r", encoding="utf-8") as file:
            html_content = file.read()
            html_content = html_content.replace("60%", study_frequency_percentage).replace("3 days/week", study_frequency)
            html_content = html_content.replace("75%", study_duration_percentage).replace("7h 30m", study_duration)
            html_content = html_content.replace("<ul></ul>", f"<ul>{focus_areas_html}</ul>")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def serve_recommended_resources_page(self, user_id):
        resources = get_resources()

        resources_html = "".join(
            f"<div class='resource-card'><span class='resource-type'>{resource['type']}</span><h3>{resource['title']}</h3><p>{resource['description']}</p><p><a href='{resource['link']}' target='_blank'>Learn more</a></p><span class='subject-badge'>{resource['subject']}</span></div>"
            for resource in resources
        )

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

# Initialize the user, achievements, progress tracking, effort levels, and resources tables
initialize_database()
initialize_achievements()
initialize_progress_tables()
initialize_effort_levels_table()
initialize_resources_table()

# Start the HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
