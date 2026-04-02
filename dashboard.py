import os
import sqlite3
import json
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windsurf_quota.db')


def get_quota_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quota_history ORDER BY timestamp ASC')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_credit_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM credit_history ORDER BY id ASC')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/sync':
            try:
                script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windsurf_quota.py')
                # Run using the same python interpreter, wait for completion
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True, text=True, timeout=300
                )
                if result.returncode == 0:
                    self._json_response({'status': 'ok', 'message': 'Sync completed'})
                else:
                    self._json_response({'status': 'error', 'message': result.stderr[-500:] or 'Unknown error'})
            except subprocess.TimeoutExpired:
                self._json_response({'status': 'error', 'message': 'Sync timed out after 5 minutes'})
            except Exception as e:
                self._json_response({'status': 'error', 'message': str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/quota':
            data = get_quota_history()
            self._json_response(data)
        elif parsed.path == '/api/credit':
            data = get_credit_history()
            self._json_response(data)
        elif parsed.path == '/' or parsed.path == '/index.html':
            self.path = '/dashboard.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def _json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[Dashboard] {args[0]}")


if __name__ == '__main__':
    port = 8050
    server = HTTPServer(('127.0.0.1', port), DashboardHandler)
    print(f"Dashboard running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
