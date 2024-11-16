import http.server
import socketserver
import urllib
import os
import mimetypes
import json
import random
from authentication import handle_login, handle_signup, fetch_user_details, update_user_info
from achievements import initialize_achievements, get_user_achievements, unlock_achievement
from progress_tracker import initialize_progress_tables, get_user_progress
from effort_tracker import initialize_effort_levels_table, get_user_effort_levels
from userDatabase import initialize_database
from flashcards import initialize_flashcards_table, get_study_sets, get_flashcards, add_study_set, add_flashcard, delete_flashcard_from_db, delete_study_set
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

import random

def get_quiz_questions_for_study_set(handler, study_set_id):
    questions = get_flashcards(study_set_id)  # Fetch all flashcards for the study set
    quiz_questions = []

    for q in questions:
        correct_answer = q['answer']
        other_answers = [flashcard['answer'] for flashcard in questions if flashcard['answer'] != correct_answer]
        distractors = random.sample(other_answers, min(len(other_answers), 3))
        options = [correct_answer] + distractors
        random.shuffle(options)

        quiz_questions.append({
            "id": q['id'],
            "question": q['question'],
            "options": options,
            "correct_answer": correct_answer
        })

    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(quiz_questions).encode("utf-8"))




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

        # New elif block for /api/get_quiz_questions
        elif self.path.startswith("/api/get_quiz_questions"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            study_set_id = params.get("study_set_id", [None])[0]
            if study_set_id:
                get_quiz_questions_for_study_set(self, int(study_set_id))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Study set ID required"}')
        
        
        elif self.path == "/api/effort_levels":
            user_ip = self.client_address[0]
            user_data = sessions.get(user_ip)
            if user_data:
                user_id = user_data.get("id")
                print(f"User ID found in session: {user_id}")
                effort_data = get_user_effort_levels(user_id)
                if effort_data:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(effort_data).encode("utf-8"))
                else:
                    # Log an explicit message if data retrieval fails
                    print(f"No effort data found for user_id: {user_id}")
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'{"error": "No effort data found"}')
            else:
                print("User not authorized for /api/effort_levels")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized"}')


                    
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

        elif self.path == '/api/delete_flashcard':
            data = parse_json_post_data(self)
            flashcard_id = data.get('flashcard_id')
            print("Received flashcard_id for deletion:", flashcard_id)  # Print to confirm ID received
            if flashcard_id:
                delete_flashcard_from_db(flashcard_id)
                print("Flashcard deleted from database with ID:", flashcard_id)  # Confirm deletion
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"message": "Flashcard deleted successfully"}')
            else:
                print("Flashcard ID is missing in the request.")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Flashcard ID required"}')

        elif self.path == '/api/submit_quiz':
            data = parse_json_post_data(self)
            study_set_id = data.get('study_set_id')
            answers = data.get('answers', [])

            if not study_set_id or not answers:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Study set ID and answers are required"}')
                return

            # Retrieve the correct answers from the database
            flashcards = get_flashcards(study_set_id)
            correct_answers = {flashcard['id']: flashcard['answer'] for flashcard in flashcards}

            # Calculate the score
            score = 0
            for answer in answers:
                question_id = answer['question_id']
                user_answer = answer['answer']
                if correct_answers.get(question_id) == user_answer:
                    score += 1

            # Return the score
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"score": score}).encode("utf-8"))

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

        elif self.path == '/api/delete_study_set':
            data = parse_json_post_data(self)
            study_set_id = data.get('study_set_id')
            if study_set_id:
                delete_study_set(int(study_set_id))  # Call the function to delete the study set
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"message": "Study set deleted successfully"}')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Study set ID required"}')

        # In the POST request handling part
        elif self.path == '/api/update_user_info':
            user_ip = self.client_address[0]
            user_data = sessions.get(user_ip)
            if not user_data:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized"}')
                return
            
            # Parse the incoming data
            data = parse_json_post_data(self)
            username = data.get('username')
            name = data.get('name')
            new_password = data.get('new_password')
            
            
            # Log the received data for debugging
            print("Received data for updating user info:", data)
            
            # Update user information in the database
            success = update_user_info(
                user_data["id"], username, name, new_password
            )

            if success:
                if username:
                    sessions[user_ip]["username"] = username
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"message": "User information updated successfully"}')
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "Failed to update user information"}')
        
        elif self.path == '/logout':
            user_ip = self.client_address[0]
            if user_ip in sessions:
                # Delete the user's session
                del sessions[user_ip]
                # Send a success response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"message": "Logged out successfully"}')
            else:
                # Send an error response if there's no session
                self.send_response(403)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "User not logged in"}')
        
        # Continue with other POST handling
        # ...



        

    def serve_account_page(self, user_data):
        # Fetch user details based on the provided username
        user_info = fetch_user_details(user_data["username"])
        
        # Open the account.html template file
        with open(os.path.join(TEMPLATES_DIR, "account.html"), 'r', encoding='utf-8') as file:
            html_content = file.read()
            
            # Replace placeholders with actual user data
            html_content = html_content.replace("<!--USERNAME_PLACEHOLDER-->", user_data["username"])  # Replace with username
            html_content = html_content.replace("John Doe", f"{user_info['first_name']} {user_info['last_name']}")  # Replace with full name
            html_content = html_content.replace("johndoe@example.com", user_info['email'])  # Replace with email

        # Send the modified HTML content to the client
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
        # Fetch user progress data
        progress_data = get_user_progress(user_id)

        # Load the HTML template for the progress page
        with open(os.path.join(TEMPLATES_DIR, "progress.html"), "r", encoding="utf-8") as file:
            html_content = file.read()
            
            # Replace placeholders for progress bars
            html_content = html_content.replace("{{STUDY_TIME_PERCENTAGE}}", str(progress_data["study_time_percentage"]))
            html_content = html_content.replace("{{STUDY_TIME_DISPLAY}}", progress_data["study_time_display"])
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_PERCENTAGE}}", str(progress_data["quiz_performance_percentage"]))
            html_content = html_content.replace("{{QUIZ_PERFORMANCE_DISPLAY}}", progress_data["quiz_performance_display"])
            
            # Embed the structured progress data as JSON in the <script> tag
            html_content = html_content.replace("{{USER_PROGRESS_DATA}}", json.dumps(progress_data))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


    def serve_effort_levels_page(self, user_id):
        print(f"Attempting to retrieve effort data for user_id: {user_id}")
        
        # Fetch effort data for the user
        effort_data = get_user_effort_levels(user_id)
        print(f"Effort data retrieved for user_id {user_id}: {effort_data}")

        if effort_data:
            study_frequency = f"{effort_data['study_frequency']} days/week"
            study_duration = f"{effort_data['study_duration'] // 60}h {effort_data['study_duration'] % 60}m"
            study_frequency_percentage = (effort_data['study_frequency'] / 7) * 100
            study_duration_percentage = (effort_data['study_duration'] / (20 * 60)) * 100

            focus_areas_html = "".join(
                f"<li><span>{subject}</span> - {percentage}% of study time</li>"
                for subject, percentage in effort_data['focus_areas'].items()
            )
        else:
            study_frequency = "No data recorded yet"
            study_duration = "No data recorded yet"
            study_frequency_percentage = 0
            study_duration_percentage = 0
            focus_areas_html = "<li>No data recorded yet</li>"

        # Load the HTML template
        template_path = os.path.join("templates", "effort-levels.html")
        print(f"Loading template from {template_path}")
        
        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        # Replace placeholders with actual values
        html_content = html_content \
            .replace("{{STUDY_FREQUENCY}}", study_frequency) \
            .replace("{{STUDY_DURATION}}", study_duration) \
            .replace("{{STUDY_FREQUENCY_PERCENTAGE}}", f"{study_frequency_percentage:.0f}") \
            .replace("{{STUDY_DURATION_PERCENTAGE}}", f"{study_duration_percentage:.0f}") \
            .replace("{{FOCUS_AREAS}}", focus_areas_html)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))
        print("Served effort levels page successfully.")



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
#initialize_effort_levels_table()
initialize_resources_table()
initialize_flashcards_table()

# Start the HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
