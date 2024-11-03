import http.server
import socketserver
from authentication import handle_login, handle_signup
from userDatabase import initialize_database
import urllib
import os
import mimetypes

PORT = 8000
TEMPLATES_DIR = 'templates'  # Directory for HTML templates
CSS_DIR = 'css'               # Directory for CSS files

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
        # Serve HTML pages from templates directory
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
            serve_page(self, os.path.join(TEMPLATES_DIR, "achievements.html"))
        elif self.path == "/progress.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "progress.html"))
        elif self.path == "/effort-levels.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "effort-levels.html"))
        elif self.path == "/recommended-sources.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "recommended-sources.html"))
        elif self.path == "/signup.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "signup.html"))
        elif self.path == "/study.html":
            serve_page(self, os.path.join(TEMPLATES_DIR, "study.html"))
        elif self.path == "/logout":
            if self.client_address[0] in sessions:
                del sessions[self.client_address[0]]
            redirect(self, '/login_screen.html')
        elif self.path.startswith("/css/"):
            # Serve CSS files from the css directory
            file_path = os.path.join(CSS_DIR, self.path[5:])  # Strip the `/css/` prefix
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'text/css'  # Default to CSS if not identified
            serve_page(self, file_path, content_type)
        else:
            super().do_GET()

    def do_POST(self):
        post_data = parse_post_data(self)

        # Handle login form submission
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
        # Load the HTML content from the template file
        with open(os.path.join(TEMPLATES_DIR, "account.html"), 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Replace placeholders in HTML with actual user data
        html_content = html_content.replace("John Doe", f"{user_data['first_name']} {user_data['last_name']}")
        html_content = html_content.replace("johndoe@example.com", user_data['email'])

        # Send response with modified HTML
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

# Helper functions
def parse_post_data(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return urllib.parse.parse_qs(post_data.decode('utf-8'))

def redirect(handler, location):
    handler.send_response(302)
    handler.send_header('Location', location)
    handler.end_headers()

# Initialize the user database
initialize_database()

# Start the HTTP server
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
