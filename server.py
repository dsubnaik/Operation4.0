import http.server
import socketserver
from authentication import handle_login, handle_signup
from userDatabase import initialize_database
import urllib
import os

PORT = 8000

TEMPLATES_DIR = 'templates'  # Directory for HTML templates

# Function to serve HTML pages
def serve_page(handler, page_name):
    try:
        with open(os.path.join(TEMPLATES_DIR, page_name), 'rb') as file:
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html')
            handler.end_headers()
            handler.wfile.write(file.read())
    except FileNotFoundError:
        handler.send_response(404)
        handler.end_headers()
        handler.wfile.write(b'Page not found')

class CustomHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/splashpage.html":
            serve_page(self, "splashpage.html")  # Serve splash page as default
        elif self.path == "/home.html":
            serve_page(self, "home.html")  # Serve 'home.html'
        elif self.path == "/login_screen.html":
            serve_page(self, "login_screen.html")  # Serve 'login_screen.html'
        elif self.path == "/flashcards.html":
            serve_page(self, "flashcards.html")  # Serve 'flashcards.html'
        elif self.path == "/quiz.html":
            serve_page(self, "quiz.html")  # Serve 'quiz.html'
        elif self.path == "/account.html":
            serve_page(self, "account.html")  # Serve 'account.html'
        elif self.path == "/achievements.html":
            serve_page(self, "achievements.html")  # Serve 'achievements.html'
        elif self.path == "/progress.html":
            serve_page(self, "progress.html")  # Serve 'progress.html'
        elif self.path == "/effort-levels.html":
            serve_page(self, "effort-levels.html")  # Serve 'effort-levels.html'
        elif self.path == "/recommended-sources.html":
            serve_page(self, "recommended-sources.html")  # Serve 'recommended-sources.html'
        elif self.path == "/signup.html":
            serve_page(self, "signup.html")  # Serve 'signup.html'
        elif self.path == "/study.html":
            serve_page(self, "study.html")  # Serve 'study.html'
        else:
            super().do_GET()

    def do_POST(self):
        post_data = parse_post_data(self)

        # Handle login form submission
        if self.path == '/login_screen.html':
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]

            if handle_login(username, password):
                redirect(self, '/home.html')  # Redirect to home page on successful login
            else:
                redirect(self, '/login_screen.html?error=1')

        # Handle registration form submission (signup)
        elif self.path == '/signup.html':
            first_name = post_data.get('first_name', [''])[0]
            last_name = post_data.get('last_name', [''])[0]
            email = post_data.get('email', [''])[0]
            username = post_data.get('username', [''])[0]
            password = post_data.get('password', [''])[0]
            confirm_password = post_data.get('confirm_password', [''])[0]

            # Check if passwords match
            if password != confirm_password:
                redirect(self, '/signup.html?error=password_mismatch')
                return

            # Add user with additional fields
            if handle_signup(username, password, first_name, last_name, email):
                redirect(self, '/home.html')  # Redirect to home page after successful signup
            else:
                redirect(self, '/signup.html?error=user_exists')

# Function to parse POST data
def parse_post_data(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return urllib.parse.parse_qs(post_data.decode('utf-8'))

# Function to handle redirection
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
