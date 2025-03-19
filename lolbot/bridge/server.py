"""Bridge server that exposes Python backend services to Electron frontend."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import multiprocessing
import datetime
import time

from lolbot.lcu.league_client import LeagueClient
from lolbot.bot.bot import Bot
from lolbot.common import config
from lolbot.system import cmd

class BridgeRequestHandler(BaseHTTPRequestHandler):
    message_queue = multiprocessing.Queue()
    games_played = multiprocessing.Value('i', 0)
    bot_errors = multiprocessing.Value('i', 0)
    bot_thread = None
    start_time = None
    
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
                phase = self.api.get_phase()
                gameTime = ""
                champ = ""
                
                if phase == "None":
                    phase = "In Main Menu"
                elif phase == "Matchmaking":
                    phase = "In Queue"
                    gameTime = self.api.get_matchmaking_time()
                elif phase == "Lobby":
                    lobby_id = self.api.get_lobby_id()
                    for lobby, lid in config.ALL_LOBBIES.items():
                        if lid == lobby_id:
                            phase = lobby + " Lobby"
                elif phase == "ChampSelect":
                    gameTime = self.api.get_cs_time_remaining()
                elif phase == "InProgress":
                    phase = "In Game"
                
                if self.bot_thread is None:
                    status = "Ready"
                    runTime = ""
                    games = 0
                    errors = 0
                else:
                    status = "Running"
                    runTime = datetime.timedelta(seconds=(time.time() - self.start_time))
                    hours, remainder = divmod(runTime.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if runTime.days > 0:
                        runTime = f"{runTime.days} day, {hours:02}:{minutes:02}:{seconds:02}"
                    else:
                        runTime = f"{hours:02}:{minutes:02}:{seconds:02}"
                    games = self.games_played.value
                    errors = self.bot_errors.value
                
                data = {
                    'phase': phase,
                    'summonerName': self.api.get_summoner_name(),
                    'summonerLevel': self.api.get_summoner_level(),
                    'gameTime': gameTime,
                    'champion': champ,
                    'status': status,
                    'runTime': runTime,
                    'games': int(games) if isinstance(games, (int, str)) and games != '-' else 0,
                    'errors': int(errors) if isinstance(errors, (int, str)) and errors != '-' else 0,
                    'isRunning': self.bot_thread is not None,
                    'logs': self.message_queue.get() if not self.message_queue.empty() else '-'
                }
                self._send_response(data)
            except Exception as e:
                self._send_response({'error': str(e)}, 500)
        elif self.path == '/api/config':
            try:
                conf = config.load_config()
                self._send_response(conf.__dict__)
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = json.loads(self.rfile.read(content_length)) if content_length else {}

        if self.path == '/api/start_bot':
            try:
                conf = config.load_config()
                if self.bot_thread is None:
                    if not (conf.windows_install_dir or conf.macos_install_dir):
                        raise Exception("League Installation Path is Invalid")
                    
                    self.message_queue.put("Clear")
                    self.start_time = time.time()
                    self.bot_thread = multiprocessing.Process(
                        target=Bot().run,
                        args=(self.message_queue, self.games_played, self.bot_errors)
                    )
                    self.bot_thread.start()
                    self._send_response({'status': 'started'})
                else:
                    self._send_response({'error': 'Bot is already running'}, 400)
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

        elif self.path == '/api/stop_bot':
            try:
                if self.bot_thread is not None:
                    self.bot_thread.terminate()
                    self.bot_thread.join()
                    self.bot_thread = None
                    self.message_queue.put("Bot Successfully Terminated")
                    self._send_response({'status': 'stopped'})
                else:
                    self._send_response({'error': 'Bot is not running'}, 400)
            except Exception as e:
                self._send_response({'error': str(e)}, 500)
                
        elif self.path == '/api/restart_ux':
            try:
                if not cmd.run(cmd.IS_CLIENT_RUNNING):
                    raise Exception("Cannot restart UX, League is not running")
                self.api.restart_ux()
                self._send_response({'status': 'restarted'})
            except Exception as e:
                self._send_response({'error': str(e)}, 500)
                
        elif self.path == '/api/close_client':
            try:
                self.message_queue.put('Closing League Processes')
                threading.Thread(target=cmd.run, args=(cmd.CLOSE_ALL,)).start()
                self._send_response({'status': 'closed'})
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

        elif self.path == '/api/config':
            try:
                conf = config.load_config()
                for key, value in post_data.items():
                    if hasattr(conf, key):
                        setattr(conf, key, value)
                config.save_config(conf)
                self._send_response({'status': 'config updated'})
            except Exception as e:
                self._send_response({'error': str(e)}, 500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=5000):
    server = HTTPServer(('localhost', port), BridgeRequestHandler)
    print(f'Bridge server running on port {port}')
    server.serve_forever()

def start_bridge_server():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    return server_thread