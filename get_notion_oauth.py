#!/usr/bin/env python3
"""Notion OAuth Token Generator for testing public integrations"""

import os
import sys
import base64
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/"

if not CLIENT_ID or not CLIENT_SECRET:
    print(" Missing OAUTH_CLIENT_ID or OAUTH_CLIENT_SECRET in .env")
    sys.exit(1)


class OAuthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        if "code" not in params:
            self._send_html(400, "<h1>No authorization code received</h1>")
            return

        code = params["code"][0]
        print(f"✓ Received code: {code[:20]}...")

        # HTTP Basic Auth: base64(client_id:client_secret)
        credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

        response = requests.post(
            "https://api.notion.com/v1/oauth/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
            },
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )

        if response.ok:
            data = response.json()
            print(f"\nAccess Token:\n{data['access_token']}")
            print(f"Workspace: {data.get('workspace_name')}")
            self._send_html(200, "<h1>Success! Check terminal.</h1>")
        else:
            print(f" Error: {response.json()}")
            self._send_html(400, f"<h1>Error</h1><p>{response.text}</p>")

    def _send_html(self, status, body):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())


if __name__ == "__main__":
    auth_url = (
        f"https://api.notion.com/v1/oauth/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&owner=user&"
        f"redirect_uri={REDIRECT_URI}"
    )

    print("Opening browser for authorization...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8000), OAuthHandler)
    print(" Waiting at http://localhost:8000/")
    server.handle_request()
