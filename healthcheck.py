"""
Tiny HTTP server that runs alongside the bot
so Fly.io health checks pass.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # silence access logs

def start():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()