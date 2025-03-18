"""Bridge server that exposes Python backend services to Electron frontend."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

from lolbot.lcu.league_client import LeagueClient
from lolbot.bot.bot import Bot
from lolbot.common import config

class BridgeRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api = LeagueClient()
        self.bot = Bot()
        super().__init__(*args, **kwargs)

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == '/api/status':
            try:
                data = {
                    'phase': self.api.get_phase(),
                    'summoner_name': self.api.get_summoner_name(),
                    'summoner_level': self.api.get_summoner_level(),
                }
                self._send_response(data)
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length)) if content_length else {}

        if self.path == '/api/start_bot':
            try:
                # Start bot logic here
                self._send_response({'status': 'started'})
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

        elif self.path == '/api/stop_bot':
            try:
                # Stop bot logic here
                self._send_response({'status': 'stopped'})
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

def run_server(port=5000):
    server = HTTPServer(('localhost', port), BridgeRequestHandler)
    print(f'Bridge server running on port {port}')
    server.serve_forever()

def start_bridge_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    return server_thread