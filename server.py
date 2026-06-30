# v2 — deploy trigger 
"""
Leafgo Client Preview — Minimal HTTP server with Basic Auth.
Deploy: Railway, single command.
"""
import http.server
import os
import base64

USERNAME = os.environ.get("AUTH_USER", "leafgo")
PASSWORD = os.environ.get("AUTH_PASS", "preview2026")
REALM = "Leafgo Vorschau"

SERVE_DIR = os.path.dirname(os.path.abspath(__file__))


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def do_HEAD(self):
        if self._check_auth():
            super().do_HEAD()

    def do_GET(self):
        if self._check_auth():
            # Clean URL redirects
            path = self.path.split('?')[0]  # strip query string
            clean_urls = {
                '/impressum': '/impressum.html',
                '/datenschutz': '/datenschutz.html',
                '/vorschau': '/form-preview.html',
            }
            if path in clean_urls:
                self.path = clean_urls[path] + ('?' + self.path.split('?')[1] if '?' in self.path else '')
            super().do_GET()

    def _check_auth(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Basic "):
            try:
                creds = base64.b64decode(auth[6:]).decode()
                user, pwd = creds.split(":", 1)
                if user == USERNAME and pwd == PASSWORD:
                    return True
            except Exception:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", f'Basic realm="{REALM}"')
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:sans-serif;padding:2em'>"
            b"<h1>Leafgo Vorschau</h1><p>Bitte Passwort eingeben.</p>"
            b"</body></html>"
        )
        return False


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = http.server.HTTPServer(("0.0.0.0", port), AuthHandler)
    print(f"🔐 Leafgo preview on :{port} (user={USERNAME})")
    server.serve_forever()
