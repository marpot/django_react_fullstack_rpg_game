import http.server
import socketserver
import os

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving documentation at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever() 