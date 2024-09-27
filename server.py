import http.server
import socketserver

PORT = 8000

# Create a request handler to serve files from the current directory
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
