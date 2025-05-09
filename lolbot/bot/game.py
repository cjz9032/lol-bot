"""
Game logic that plays and through a single League of Legends match.
"""

import logging
import random
from time import sleep
from datetime import datetime, timedelta
import json
from typing import Callable
import sys

from lolbot.lcu.game_server import GameServer, GameServerError
from lolbot.system import mouse, keys, window, cmd, OS

log = logging.getLogger(__name__)

# Game Times
LOADING_SCREEN_TIME = 3
MINION_CLASH_TIME = 85
GROW_TIME = 300
FIRST_TOWER_TIME = 600
MAX_GAME_TIME = 2400

# Click coordinates to move/aim
MINI_MAP_UNDER_TURRET = (0.88, 0.90)
MINI_MAP_CENTER_MID = (0.9035, 0.87)
# 933 664
MINI_MAP_GROW_ATTACK = (0.9035, 0.87)
MINI_MAP_CENTER_MID_ATTACK = (0.92, 0.85)
MINI_MAP_ENEMY_NEXUS = (0.9678, 0.7852)
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
FACE_FRONT = (0.6564, 0.2755)
FACE_END = (0.35, 0.65)

MAX_SERVER_ERRORS = 15

GLOBAL_CHAMP = 0

win_x = 0
win_y = 0
win_l = 0
win_h = 0
from lolbot.common import config

class GameError(Exception):
    """Indicates the game should be terminated"""
    pass

config = config.load_config()

def disableLCU() -> bool:
    # return OS == "Windows" and config.riot
    return False

def isWinRiot() -> bool:
    return OS == "Windows" and config.riot

hasLocked = False

def play_game(champ: int) -> None:
    """Plays a single game of League of Legends, takes actions based on game time"""
    global GLOBAL_CHAMP
    global hasLocked
    GLOBAL_CHAMP = champ
    log.info(f"play game " + str(champ))
    game_server = GameServer()
    try:
        hasLocked = False
        wait_for_game_window()
        wait_for_connection(game_server)
        init_game_window()
        if OS == 'Windows':
            window.bring_to_front(window.GAME_WINDOW)
        left_click(CENTER_OF_SCREEN)
        game_loop(game_server)
    except GameError as e:
        log.error(e)
        cmd.run(cmd.CLOSE_ALL)
        hasLocked = False
        log.error("check above error Exiting")
        sys.exit()
        return
    except window.WindowNotFound:
        log.info(f"Game Complete")


def wait_for_game_window() -> None:
    """Loop that waits for game window to open"""
    for i in range(120):
        sleep(1)
        try:
            if window.check_window_exists(window.GAME_WINDOW):
                log.info("Game Launched")
                sleep(3)
                if OS == 'Windows':
                    window.bring_to_front(window.GAME_WINDOW)
                sleep(3)
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


_nowTime = datetime.now()
_gameTime = 0

def syncGameTime(new:int) -> None:
    global _gameTime
    global _nowTime
    _gameTime = new
    _nowTime = datetime.now()

def getGameTime(game_server: GameServer)-> int:
    if disableLCU():
        return (datetime.now() - _nowTime).total_seconds() + _gameTime
    else:
        return game_server.get_game_time()
    

def get_summoner_health(game_server: GameServer)-> float:
    if disableLCU():
        return 1.0
    else:
        return game_server.get_summoner_health()

def summoner_is_dead(game_server: GameServer)-> bool:
    if disableLCU():
        # 325 7xx
        coords = window.convert_ratio_abs((0.3173,0.9648), win_x, win_y, win_l, win_h)
        return window.is_color_close_by_xy(coords)
    else:
        return game_server.summoner_is_dead()


lastGold = 0
lastGoldErr = 0
lastCheckTime = 0
def detectOffline(game_server: GameServer) -> None:
    if disableLCU(): 
        return
    global lastGold, lastGoldErr, lastCheckTime
    game_time = game_server.get_game_time()
    if game_time - lastCheckTime < 10:
        return
    
    lastCheckTime = game_time

    
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
        log.info("Game State unchanged might be crashed")
        raise GameError("Game State unchanged might be crashed")
    


def game_loop(game_server: GameServer) -> None:
    global hasLocked
    hasLocked = False
    server_errors = 0
    global lastGold, lastGoldErr

    game_time = game_server.get_game_time()
    syncGameTime(game_time)
    if isWinRiot():
        log.info("CLOSE_VGC")
        cmd.run(cmd.CLOSE_VGC)


    lastGold = 0
    lastGoldErr = 0
    checkDiedCounts = 0

    try:
        while True:
            # Don't start new sequence when dead
            if summoner_is_dead(game_server):
                sleep(5)
                shop(game_server)
                checkDiedCounts += 1
                if checkDiedCounts > 12:
                    cmd.run(cmd.CLOSE_ALL)
                    log.error("offline died detect Exiting")
                    sys.exit()
                    return
                detectOffline(game_server)
                continue
            checkDiedCounts = 0
            upgrade_abilities()

            # Take action based on game time
            game_time = getGameTime(game_server)
            if game_time < LOADING_SCREEN_TIME:
                loading_screen(game_server)
            elif game_time < MINION_CLASH_TIME:
                game_start(game_server)
            elif game_time < GROW_TIME:
                play(game_server, MINI_MAP_GROW_ATTACK, MINI_MAP_UNDER_TURRET, 20, game_time)
            elif game_time < FIRST_TOWER_TIME:
                play(game_server, MINI_MAP_CENTER_MID_ATTACK, MINI_MAP_UNDER_TURRET, 20, game_time)
            elif game_time < MAX_GAME_TIME:
                play(game_server, MINI_MAP_ENEMY_NEXUS, MINI_MAP_CENTER_MID, 35, game_time)
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
    global hasLocked
    log.info("Waiting for Minion Clash")
    sleep(10)
    keypress('y')  # lock screen
    hasLocked = True
    upgrade_abilities()
    # Sit under turret till minions clash mid lane
    while getGameTime(game_server) < MINION_CLASH_TIME:
        right_click(MINI_MAP_UNDER_TURRET)  # to prevent afk warning popup
        left_click(AFK_OK_BUTTON)
    log.info("Playing Game")

def signal():
    if random.uniform(0, 100) > 80:
        keypress('v')
        left_click(FACE_FRONT)
        keypress('g')
        left_click(FACE_FRONT)
    keypress('u')

def play(game_server: GameServer, attack_position: tuple, retreat: tuple, time_to_lane: int, game_time: int) -> None:
    global GLOBAL_CHAMP
    global hasLocked
    if not hasLocked:
        keypress('y')  # lock screen
        hasLocked = True
    """Buys items, levels up abilities, heads to lane, attacks, retreats, backs"""
    shop(game_server)
    upgrade_abilities()
    left_click(AFK_OK_BUTTON)

    # Walk to lane
    if GLOBAL_CHAMP == 33:
        keypress('q')

    attack_click(attack_position)
    keypress('d')  # ghost
    sleep(time_to_lane/1.5)


    # Main attack move loop. This sequence attacks and then de-aggros to prevent them from dying 50 times.
    l_game_time = getGameTime(game_server)

    for i in range(60):
        if random.uniform(0, 100) > 50:
            detectOffline(game_server)
        
        hc = get_summoner_health(game_server)
        # mono = int(json.loads(game_server.data)['activePlayer']['currentGold'])
        #  or (False if  l_game_time > 1200 else mono > 4000)
        
        if (l_game_time > FIRST_TOWER_TIME if hc < .01 else hc < .1):
            keypress('f')
            right_click(retreat)
            sleep(3)
            break
        if summoner_is_dead(game_server):
            return
        
     
        if GLOBAL_CHAMP == 67:
            if random.uniform(0, 100) > 90:
                right_click(FACE_END, 0.2)

            for i in range(1, 2):
                attack_click(attack_position)
                move(FACE_END)
                keypress('q')
                sleep(1)
        elif GLOBAL_CHAMP == 18:
            attack_click(attack_position)
            for i in range(1, 15):
                move((0.3+random.uniform(0, 0.4), 0.1+random.uniform(0, 0.3)), 0)
                keypress('e', 0)
            keypress('q')
            if random.uniform(0, 100) > 80:
                move((0.3, 0.75))
                keypress('w')
        elif GLOBAL_CHAMP == 15:
            for i in range(1, 3):
                keypress('w')
                move(FACE_FRONT)
                keypress('q')
                keypress('e')
                if random.uniform(0, 100) > 70:
                    keypress('r')
                attack_click(attack_position)
        elif GLOBAL_CHAMP == 10:
            for i in range(1, 4):
                self_press('w')
                move(FACE_FRONT)
                keypress('q')
                keypress('e')
                attack_click(attack_position)
                hc = get_summoner_health(game_server)
                if hc < .5:
                    self_press('r')
        elif GLOBAL_CHAMP == 222:
            attack_click(attack_position)
            sleep(1)
            if random.uniform(0, 100) > 80:
                keypress('q')
            if random.uniform(0, 100) > 80:
                right_click(FACE_END, 0.2)
            attack_click(attack_position)
            move(FACE_FRONT)
            sleep(2)
        elif GLOBAL_CHAMP == 11:
            attack_click(attack_position)
            for i in range(1, 12):
                move((0.35+random.uniform(0, 0.35), 0.25+random.uniform(0, 0.35)), 0)
                keypress('q', 0)
            keypress('e')
            keypress('w', 0)
            attack_click(attack_position)
        elif GLOBAL_CHAMP == 17:
            attack_click(attack_position)
            move((0.7+random.uniform(0, 0.2), 0.2+random.uniform(0, 0.3)), 0.1)
            keypress('r')
        elif GLOBAL_CHAMP == 122:
            attack_click(attack_position)
            sleep(1)
            right_click(FACE_END)
            keypress('q')
            attack_click(attack_position)
            keypress('w')
            for i in range(1, 3):
                move((0.5+random.uniform(0, 0.1), 0.35 + i*0.1), 0.05)
                keypress('r', 0.05)
        elif GLOBAL_CHAMP == 54:
            for i in range(1, 2):
                keypress('w')
                keypress('e')
                attack_click(attack_position)
        elif GLOBAL_CHAMP == 33:
            for i in range(1, 3):
                move((0.5+random.uniform(0, 0.1), 0.35 + i*0.1), 0.05)
                keypress('e', 0.05)
            keypress('w')
            if random.uniform(0, 100) > 80:
                move(FACE_FRONT)
                keypress('r')
            attack_click(attack_position)
            sleep(8)
        else:
            attack_click(attack_position)
            move((0.6+random.uniform(0, 0.3), 0.2+random.uniform(0, 0.2)), 0.1)
            keypress('e')
            keypress('q')
            keypress('w')

        if random.uniform(0, 100) > 80:
            move(FACE_FRONT)
            keypress('r')


        if random.uniform(0, 100) > 50:
            move(FACE_FRONT)
            for i in range(1, 8):
                keypress(str(i), 0)
           
        if random.uniform(0, 100) > 90:
            move(FACE_FRONT)
            signal()

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


def shop(game_server: GameServer) -> None:
    curGold = int(json.loads(game_server.data)['activePlayer']['currentGold'])
    if curGold < 1000:
        return

    """Opens the shop and attempts to purchase items via default shop hotkeys"""
    keypress('p')  # open shop
    sleep(1)
    left_click((0.5478, 0.1971))
    game_time2 = game_server.get_game_time()

    max_num = 2
    if game_time2 > 1200:
        max_num = 6
    elif game_time2 > 900:
        max_num = 5
    elif game_time2 > 600:
        max_num = 4

    # repeat to click one
    for i in range(max_num):
        left_click((0.2434 + (0.0391 * (i)), 0.3710), 0.1)
        left_click(SHOP_PURCHASE_ITEM_BUTTON, 0.1)
    # keypress('esc')
    sleep(1)
    left_click(SHOP_CLOSE, .3)
    left_click(SYSTEM_MENU_X_BUTTON)


def upgrade_abilities() -> None:
    global GLOBAL_CHAMP
    window.check_window_exists(window.GAME_WINDOW)

    if GLOBAL_CHAMP == 17:
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+e')
        keys.press_and_release('ctrl+w')
    if GLOBAL_CHAMP == 33:
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+e')
    if GLOBAL_CHAMP == 10:
        keys.press_and_release('ctrl+e')
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+w')
    if GLOBAL_CHAMP == 15:
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+q')
    if GLOBAL_CHAMP == 67:
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+q')
    if GLOBAL_CHAMP == 54:
        keys.press_and_release('ctrl+w')
        keys.press_and_release('ctrl+e')
        keys.press_and_release('ctrl+r')
    if GLOBAL_CHAMP == 11:
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+e')

    if GLOBAL_CHAMP == 18:
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+e')

    if GLOBAL_CHAMP == 222:
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+r')

    if GLOBAL_CHAMP == 122:
        keys.press_and_release('ctrl+r')
        keys.press_and_release('ctrl+q')
        keys.press_and_release('ctrl+e')

    upgrades = ['ctrl+r', 'ctrl+w', 'ctrl+e','ctrl+q', 'ctrl+w', 'ctrl+e']
    random.shuffle(upgrades)
    for upgrade in upgrades:
        keys.press_and_release(upgrade)

def init_game_window() -> None:
    global win_x
    global win_y
    global win_l
    global win_h
    win_x, win_y, win_l, win_h = window.get_window_size(window.GAME_WINDOW)

def left_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio_abs(ratio, win_x, win_y, win_l, win_h)
    mouse.move(coords, 0.2)
    mouse.left_click(delay)

def left_db_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio_abs(ratio, win_x, win_y, win_l, win_h)
    mouse.move(coords, 0.2)
    mouse.left_db_click(delay)

def right_click(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio_abs(ratio, win_x, win_y, win_l, win_h)
    mouse.move(coords, 0.2)
    mouse.right_click(delay)


def attack_click(ratio: tuple) -> None:
    coords = window.convert_ratio_abs(ratio, win_x, win_y, win_l, win_h)
    mouse.move(coords, 0.2)
    keys.key_down('a')
    sleep(.1)
    mouse.left_click()
    sleep(.1)
    mouse.left_click()
    keys.key_up('a')
    sleep(.2)

def move(ratio: tuple, delay = 0.2) -> None:
    coords = window.convert_ratio_abs(ratio, win_x, win_y, win_l, win_h)
    mouse.move(coords, delay)

def keypress(key: str, delay = 0.2) -> None:
    keys.press_and_release(key)
    if delay > 0:
        sleep(delay)

def self_press(key: str, delay = 0.2) -> None:
    keys.key_self_press(key)
    if delay > 0:
        sleep(delay)
