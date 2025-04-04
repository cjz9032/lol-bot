import subprocess
import re
import os
import sys
from time import sleep
import logging

log = logging.getLogger(__name__)

# Regex
LCU_PORT_KEY = "--app-port="
LCU_TOKEN_KEY = "--remoting-auth-token="
PORT_REGEX = re.compile(r"--app-port=(\d+)")
TOKEN_REGEX = re.compile(r"--remoting-auth-token=(\S+)")

# Commands
LAUNCH_CLIENT = 'open "/Applications/League of Legends.app"'
LAUNCH_SPEEED = 'open "/Applications/UUBooster.app"'

IS_GAME_RUNNING = 'pgrep -fl "LeagueOfLegends.app"'
IS_CLIENT_RUNNING = 'pgrep -fl "LeagueClient" | grep -v "Riot"'
IS_LAUNCHER_RUNNING = 'pgrep -fl "Riot"'

CLOSE_GAME = 'kill -9 $(pgrep -f "LeagueOfLegends.app")'
CLOSE_CLIENT = 'kill -9 $(pgrep -f "LeagueClient")'
CLOSE_LAUNCHER = 'kill -9 $(pgrep -f "Riot")'
CLOSE_SPEED = 'kill -9 $(pgrep -f "UUBooster.app")'
CLOSE_ALL = 'kill -9 $(pgrep -f "League");' + CLOSE_LAUNCHER + ';' + CLOSE_SPEED


def run(command: str) -> bool:
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.returncode == 0


def get_auth_string() -> str:
    result = subprocess.run(IS_CLIENT_RUNNING, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        result = subprocess.run(IS_LAUNCHER_RUNNING, shell=True, text=True, capture_output=True)
    stdout = result.stdout

    port_match = PORT_REGEX.search(stdout)
    port = port_match.group(1).replace(LCU_PORT_KEY, '') if port_match else "0"

    token_match = TOKEN_REGEX.search(stdout)
    token = token_match.group(1).replace(LCU_TOKEN_KEY, '').replace('"', '') if token_match else ""

    return f"https://riot:{token}@127.0.0.1:{port}"


def restart_program():
    run(CLOSE_ALL)
    """Restart the program"""
    log.info('restart...')
    python = sys.executable
    os.execl(python, python, *sys.argv)
    sleep(3)
    # Close current program
    sys.exit()