"""
Handles launching League of Legends and logging into an account.
"""
import logging
from lolbot.lcu import game_server

log = logging.getLogger(__name__)


class FZ:

    def __init__(self):
        self.game_server = game_server.GameServer()

    def monitorHealth(self):
        self.game_server.get_summoner_health()