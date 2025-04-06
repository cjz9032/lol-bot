"""
Game logic that plays and through a single League of Legends match.
"""

import logging
import random
from time import sleep
from datetime import datetime, timedelta
import json

from lolbot.lcu.game_server import GameServer, GameServerError
from lolbot.system import mouse, keys, window, cmd

log = logging.getLogger(__name__)

# Game Times
LOADING_SCREEN_TIME = 3
MINION_CLASH_TIME = 85
GROW_TIME = 600
FIRST_TOWER_TIME = 700
MAX_GAME_TIME = 2000

# Click coordinates to move/aim
MINI_MAP_UNDER_TURRET = (0.88, 0.90)
MINI_MAP_CENTER_MID = (0.9035, 0.87)
# 933 664
MINI_MAP_GROW_ATTACK = (0.9035, 0.87)
MINI_MAP_CENTER_MID_ATTACK = (0.92, 0.85)
MINI_MAP_ENEMY_NEXUS = (0.9628, 0.7752)
ULT_DIRECTION = (0.7298, 0.2689)
CENTER_OF_SCREEN = (0.5, 0.5)

# Click coordinates to purchase items
AFK_OK_BUTTON = (0.4981, 0.4647)
SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)
# SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
# fixed at first 220 270 315, 580 , (0.2636, 0.7552), (0.3076, 0.7552), (0.3564, 0.7552) 
SHOP_ITEM_BUTTONS = [(0.2148, 0.7552)] 
SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.58)
# 912 143
SHOP_CLOSE = (0.8906, 0.1861)
# 580 227
FACE_FRONT = (0.5564, 0.2755)
FACE_END = (0.35, 0.65)

MAX_SERVER_ERRORS = 15

GLOBAL_CHAMP = 0

class GameError(Exception):
    """Indicates the game should be terminated"""
    pass

def play_game(champ: int) -> None:
    """Plays a single game of League of Legends, takes actions based on game time"""
    global GLOBAL_CHAMP
    GLOBAL_CHAMP = champ
    game_server = GameServer()
    try:
        wait_for_game_window()
        wait_for_connection(game_server)
        game_loop(game_server)
    except GameError as e:
        log.warning(e)
        cmd.run(cmd.CLOSE_GAME)
        sleep(30)
    except window.WindowNotFound:
        log.info(f"Game Complete")


def wait_for_game_window() -> None:
    """Loop that waits for game window to open"""
    for i in range(120):
        sleep(1)
        try:
            if window.check_window_exists(window.GAME_WINDOW):
                log.info("Game Launched")
                left_click(CENTER_OF_SCREEN)
                left_click(CENTER_OF_SCREEN)
                return
        except window.WindowNotFound:
            pass
    raise GameError("Game window did not open")


def wait_for_connection(game_server: GameServer) -> None:
    for i in range(120):
        if game_server.is_running():
            return
        sleep(1)
    raise GameError("Game window opened but connection failed")



def game_loop(game_server: GameServer) -> None:
    game_time = 0
    server_errors = 0
    lastGold = 0
    lastGoldErr = 0

    def detectOffline() -> None:
        nonlocal lastGold, lastGoldErr, server_errors
        if game_time > MINION_CLASH_TIME:
            curGold = int(json.loads(game_server.data)['activePlayer']['currentGold'])
            if curGold == lastGold:
                log.info(f"Game State unchanged lastGoldErr {lastGoldErr}")
                lastGoldErr += 1
            else:
                lastGold = curGold
                log.info(f"Game State changed lastGold {lastGold}")

                lastGoldErr = 0
        if lastGoldErr == 1:
            server_errors = MAX_SERVER_ERRORS
            log.info("Game State unchanged might be crashed")
            raise GameError("Game State unchanged might be crashed")
        
    try:
        while True:
            # Don't start new sequence when dead
            if game_server.summoner_is_dead():
                shop()
                upgrade_abilities()
                sleep(3)
                continue

            # Take action based on game time
            game_time = game_server.get_game_time()
            detectOffline()
            if game_time < LOADING_SCREEN_TIME:
                loading_screen(game_server)
            elif game_time < MINION_CLASH_TIME:
                game_start(game_server)
            elif game_time < GROW_TIME:
                play(game_server, MINI_MAP_GROW_ATTACK, MINI_MAP_UNDER_TURRET, 20)
            elif game_time < FIRST_TOWER_TIME:
                play(game_server, MINI_MAP_CENTER_MID_ATTACK, MINI_MAP_UNDER_TURRET, 20)
            elif game_time < MAX_GAME_TIME:
                play(game_server, MINI_MAP_ENEMY_NEXUS, MINI_MAP_CENTER_MID, 35)
            else:
                raise GameError("Game has exceeded the max time limit")
    except GameServerError as e:
        server_errors += 1
        if server_errors == MAX_SERVER_ERRORS:
            raise GameError(f"Max Server Errors reached: {e}")


def loading_screen(game_server: GameServer) -> None:
    log.info("In Loading Screen")
    start = datetime.now()
    while game_server.get_game_time() < LOADING_SCREEN_TIME:
        sleep(2)
        if datetime.now() - start > timedelta(minutes=10):
            raise GameError("Loading screen max time limit exceeded")
    left_click(CENTER_OF_SCREEN)
    log.info("Game Started")


def game_start(game_server: GameServer) -> None:
    """Buys starter items and waits for minions to clash (minions clash at 90 seconds)"""
    log.info("Waiting for Minion Clash")
    sleep(10)
    keypress('y')  # lock screen
    upgrade_abilities()

    # Sit under turret till minions clash mid lane
    while game_server.get_game_time() < MINION_CLASH_TIME:
        right_click(MINI_MAP_UNDER_TURRET)  # to prevent afk warning popup
        left_click(AFK_OK_BUTTON)
    log.info("Playing Game")


def play(game_server: GameServer, attack_position: tuple, retreat: tuple, time_to_lane: int, excited: bool = False) -> None:
    global GLOBAL_CHAMP
    """Buys items, levels up abilities, heads to lane, attacks, retreats, backs"""
    shop()
    upgrade_abilities()
    left_click(AFK_OK_BUTTON)

    # Walk to lane
    attack_click(attack_position)
    keypress('d')  # ghost
    sleep(time_to_lane/2)

    # Main attack move loop. This sequence attacks and then de-aggros to prevent them from dying 50 times.
    l_game_time = game_server.get_game_time()

    for i in range(60):
        hc = game_server.get_summoner_health()
        if (l_game_time > FIRST_TOWER_TIME if hc < .01 else hc < .1) or (int(json.loads(game_server.data)['activePlayer']['currentGold']) > 4000):
            keypress('f')
            right_click(retreat)
            sleep(3)
            break
        if game_server.summoner_is_dead():
            return
        
     
        if GLOBAL_CHAMP == 67:
            attack_click(attack_position)
            move(FACE_END)
            keypress('q')
        elif GLOBAL_CHAMP == 18:
            attack_click(attack_position)
            for i in range(1, 4):
                move((0.5+random.uniform(0, 0.2), 0.2+random.uniform(0, 0.2)), 0.1)
                keypress('e', 0.1)
            keypress('q')
            sleep(1)
            move((0.3, 0.75))
            keypress('w')
        else:
            attack_click(attack_position)
            move((0.5564+random.uniform(0, 0.1), 0.2755+random.uniform(0, 0.1)))
            keypress('e')
            keypress('q')
            keypress('w')
            
        if random.uniform(0, 100) > 80:
            keypress('r')

        for i in range(1, 8):
            keypress(str(i), 0.1)
            
        
    if game_server.summoner_is_dead():
        return
    # if not excited:
    # Ult and back
    # attack_click(ULT_DIRECTION)
    # sleep(1)
    right_click(MINI_MAP_UNDER_TURRET)
    sleep(4)
    keypress('b')
    sleep(9)


def shop() -> None:
    """Opens the shop and attempts to purchase items via default shop hotkeys"""
    keypress('p')  # open shop
    # repeat to click one
    for i in range(1):
        left_db_click(random.choice(SHOP_ITEM_BUTTONS), 0.1)
        left_click(SHOP_PURCHASE_ITEM_BUTTON, 0.1)
    # keypress('esc')
    left_click(SHOP_CLOSE)
    left_click(SYSTEM_MENU_X_BUTTON)


def upgrade_abilities() -> None:
    global GLOBAL_CHAMP
    window.check_window_exists(window.GAME_WINDOW)
    if GLOBAL_CHAMP == 67:
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+q')

    if GLOBAL_CHAMP == 18:
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+e')

    upgrades = ['ctrl+q', 'ctrl+w', 'ctrl+e','ctrl+q', 'ctrl+w', 'ctrl+e']
    random.shuffle(upgrades)
    for upgrade in upgrades:
        keys.press_and_release(upgrade)


def left_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    mouse.left_click()
    sleep(delay)

def left_db_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    mouse.left_db_click()
    sleep(delay)

def right_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    mouse.right_click()
    sleep(delay)


def attack_click(ratio: tuple) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    keys.key_down('a')
    sleep(.1)
    mouse.left_click()
    sleep(.1)
    mouse.left_click()
    keys.key_up('a')
    sleep(.6)

def move(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords, delay)

def keypress(key: str, delay = 0.2) -> None:
    window.check_window_exists(window.GAME_WINDOW)
    keys.press_and_release(key)
    sleep(delay)
