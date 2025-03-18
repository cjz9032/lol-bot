"""
Controls the League Client and continually starts League of Legends games.
"""
import shutil
import logging
import multiprocessing as mp
import os
import random
import configparser
import json
import traceback
from datetime import datetime, timedelta
from time import sleep

from lolbot.bot import game, launcher
from lolbot.system import mouse, window, cmd, OS
from lolbot.common import accounts, config, logger
from lolbot.lcu.league_client import LeagueClient, LCUError

log = logging.getLogger(__name__)

# Click Ratios
POST_GAME_OK_RATIO = (0.4996, 0.9397)
POST_GAME_SELECT_CHAMP_RATIO = (0.4977, 0.5333)
POPUP_SEND_EMAIL_X_RATIO = (0.6960, 0.1238)

# Errors
MAX_BOT_ERRORS = 5
MAX_PHASE_ERRORS = 999


class BotError(Exception):
    """Indicates the League Client instance should be restarted."""
    pass


class Bot:
    """Handles the League Client and all tasks needed to start a new game."""

    def __init__(self) -> None:
        self.api = LeagueClient()
        self.launcher = launcher.Launcher()
        self.config = config.load_config()
        self.max_level = self.config.max_level
        self.lobby = self.config.lobby
        self.account = None
        self.phase = None
        self.prev_phase = None
        self.bot_errors = 0
        self.phase_errors = 0

    def run(self, message_queue: mp.Queue, games: mp.Value, errors: mp.Value) -> None:
        """Main loop, gets an account, launches league, monitors account level, and repeats."""
        logger.MultiProcessLogHandler(message_queue).set_logs()
        self.api.update_auth_timer()
        self.print_ascii()
        while True:
            try:
                errors.value = self.bot_errors
                self.account = accounts.get_account(self.max_level)
                self.launcher.launch_league(self.account["username"], self.account["password"])
                self.wait_for_patching()
                self.set_game_config()
                self.leveling_loop(games)
                cmd.run(cmd.CLOSE_ALL)
                self.bot_errors = 0
                self.phase_errors = 0
            except BotError as be:
                log.error(be)
                self.bot_errors += 1
                self.phase_errors = 0
                if self.bot_errors == MAX_BOT_ERRORS:
                    log.error("Max errors reached. Exiting")
                    return
                else:
                    cmd.run(cmd.CLOSE_ALL)
            except launcher.LaunchError as le:
                log.error(le)
                log.error("Launcher Error. Exiting")
                return
            except Exception as e:
                log.error(e)
                if traceback.format_exc() is not None:
                    log.error(traceback.format_exc())
                log.error("Unknown Error. Exiting")
                return

    def leveling_loop(self, games: mp.Value) -> None:
        """Loop that takes action based on the phase of the League Client, continuously starts games."""
        while not self.account_leveled():
            match self.get_phase():
                case "None" | "Lobby":
                    self.start_matchmaking()
                case "Matchmaking":
                    self.queue()
                case "ReadyCheck":
                    self.accept_match()
                case "ChampSelect":
                    self.champ_select()
                case "InProgress":
                    game.play_game()
                case "Reconnect":
                    self.reconnect()
                case "WaitingForStats":
                    self.wait_for_stats()
                case "PreEndOfGame":
                    self.pre_end_of_game()
                case "EndOfGame":
                    self.end_of_game()
                    games.value += 1
                case _:
                    raise BotError("Unknown phase. {}".format(self.phase))

    def get_phase(self) -> str:
        """Requests the League Client phase."""
        err = None
        for i in range(15):
            try:
                self.prev_phase = self.phase
                self.phase = self.api.get_phase()
                if (
                    self.prev_phase == self.phase
                    and self.phase != "Matchmaking"
                    and self.phase != "ReadyCheck"
                ):
                    self.phase_errors += 1
                    if self.phase_errors == MAX_PHASE_ERRORS:
                        raise BotError("Transition error. Phase will not change")
                else:
                    self.phase_errors = 0
                sleep(1.5)
                return self.phase
            except LCUError as e:
                err = e
        raise BotError(f"Could not get phase: {err}")

    def start_matchmaking(self) -> None:
        """Starts matchmaking for a particular game mode, will also wait out dodge timers."""
        # reset again 
        self.set_game_config()
        # Create lobby
        lobby_name = ""
        for lobby, lid in config.ALL_LOBBIES.items():
            if lid == self.lobby:
                lobby_name = lobby + " "
        log.info(f"Creating {lobby_name.lower()}lobby")
        try:
            self.api.create_lobby(self.lobby)
            sleep(3)
        except LCUError:
            return

        # Start Matchmaking
        log.info("Starting queue")
        try:
            self.api.start_matchmaking()
            sleep(1)
        except LCUError:
            return

        # Wait out dodge timer
        try:
            time_remaining = self.api.get_dodge_timer()
            if time_remaining > 0:
                log.info(f"Dodge Timer. Time Remaining: {time_remaining}")
                sleep(time_remaining)
        except LCUError:
            return

        # TODO when queue times get too high switch to pvp lobby, start it, and then switch back

    def queue(self) -> None:
        """Waits until the League Client Phase changes to something other than 'Matchmaking'."""
        log.info("Waiting for Ready Check")
        start = datetime.now()
        while True:
            try:
                if self.api.get_phase() != "Matchmaking":
                    return
                elif datetime.now() - start > timedelta(minutes=15):
                    raise BotError("Queue Timeout")
                sleep(1)
            except LCUError:
                sleep(1)

    def accept_match(self) -> None:
        """Accepts the Ready Check."""
        try:
            if self.prev_phase != "ReadyCheck":
                log.info("Accepting Match")
            self.api.accept_match()
        except LCUError:
            pass

    def champ_select(self) -> None:
        """Handles the Champ Select Lobby."""
        log.info("Locking in champ")
        logged = False
        champ = ""
        # https://darkintaqt.com/blog/champ-ids 67, 222, 202, 21
        # priority_champs = [18] # 小跑
        priority_champs = [67] # VN
        tried = False
        while True:
            try:
                data = self.api.get_champ_select_data()
                champ_list = self.api.get_available_champion_ids()
            except LCUError:
                return
            try:
                for action in data["actions"][0]:
                    if action["actorCellId"] == data["localPlayerCellId"]:
                        if action["championId"] == 0:  # No champ hovered. Hover a champion.
                            # log.info(f"No champ hovered : champ_list {champ_list}")
                            available_priority_champs = [champ for champ in champ_list if champ in priority_champs]
                            log.info(f"No champ hovered : available_priority_champs {available_priority_champs}")
                            if available_priority_champs and (not tried):
                                champ = random.choice(available_priority_champs)
                            else:
                                champ = random.choice(champ_list)
                            log.info(f"will hover : {champ}")
                            self.api.hover_champion(action["id"], champ)
                            tried = True
                        elif not action["completed"]:  # Champ is hovered but not locked in.
                            tried = True
                            self.api.lock_in_champion(action["id"], action["championId"])
                        else:  # Champ is locked in. Nothing left to do.
                            tried = True
                            if not logged:
                                log.info(f"Locked in: {champ}")
                                log.info("Waiting for game to launch")
                                logged = True
                            sleep(2)
            except LCUError:
                pass

    def reconnect(self) -> None:
        """Attempts to reconnect to an ongoing League of Legends match."""
        log.info("Reconnecting to game")
        for i in range(3):
            try:
                self.api.game_reconnect()
                sleep(3)
                return
            except LCUError:
                sleep(2)
        log.warning("Could not reconnect to game")

    def wait_for_stats(self) -> None:
        """Waits for the League Client Phase to change to something other than 'WaitingForStats'."""
        log.info("Waiting for stats")
        for i in range(60):
            sleep(2)
            try:
                if self.api.get_phase() != "WaitingForStats":
                    return
            except LCUError:
                pass
        raise BotError("Waiting for stats timeout")

    def pre_end_of_game(self) -> None:
        """Handles league of legends client reopening after a game, honoring teammates, and clearing level-up/mission rewards."""
        log.info("Honoring teammates and accepting rewards")
        sleep(10)
        popup_x_coords = window.convert_ratio(POPUP_SEND_EMAIL_X_RATIO, window.CLIENT_WINDOW)
        select_champ_coords = window.convert_ratio(POST_GAME_SELECT_CHAMP_RATIO, window.CLIENT_WINDOW)
        ok_button_coords = window.convert_ratio(POST_GAME_OK_RATIO, window.CLIENT_WINDOW)
        try:
            mouse.move_and_click(popup_x_coords)
            if not self.honor_player():
                sleep(60)  # Honor failed for some reason, wait out the honor screen
            mouse.move_and_click(popup_x_coords)
            for i in range(3):
                mouse.move_and_click(select_champ_coords)
                mouse.move_and_click(ok_button_coords)
            mouse.move_and_click(popup_x_coords)
        except window.WindowNotFound:
            sleep(3)

    def honor_player(self) -> bool:
        """Honors a player in the post game lobby. There are no enemies to honor in bot lobbies."""
        for i in range(3):
            try:
                players = self.api.get_players_to_honor()
                index = random.randint(0, len(players) - 1)
                self.api.honor_player(players[index]["summonerId"])
                sleep(2)
                return True
            except LCUError as e:
                log.warning(e)
        log.warning("Honor Failure")
        return False

    def end_of_game(self) -> None:
        """Transitions out of EndOfGame."""
        log.info("Starting new game")
        posted = False
        for i in range(15):
            try:
                if self.api.get_phase() != "EndOfGame":
                    return
                if not posted:
                    self.api.play_again()
                else:
                    self.start_matchmaking()
                posted = not posted
                sleep(1)
            except LCUError:
                pass
        raise BotError("Could not exit play-again screen")

    def account_leveled(self) -> bool:
        """Checks if account has reached max level."""
        try:
            if self.api.get_summoner_level() >= self.max_level:
                if self.account["username"] == self.api.get_summoner_name():
                    self.account["level"] = self.max_level
                    accounts.save_or_add(self.account)
                log.info("Account successfully leveled")
                return True
            return False
        except LCUError:
            return False

    def wait_for_patching(self) -> None:
        """Checks if the League Client is patching and waits till it is finished."""
        log.info("Checking for Client Updates")
        logged = False
        while self.api.is_client_patching():
            if not logged:
                log.info("Client is patching...")
                logged = True
            sleep(3)
        log.info("Client is up to date")

    def set_game_config(self) -> None:
        """Overwrites the League of Legends game config."""
        log.info("Overwriting game configs")
        if OS == 'Windows':
            config_dir = os.path.join(self.config.windows_install_dir, 'Config')
        else:
            config_dir = os.path.join(self.config.macos_install_dir, 'contents/lol/config')
        game_config = os.path.join(config_dir, 'game.cfg')
        input_config = os.path.join(config_dir, 'input.ini')
        current_dir = os.path.dirname(__file__)
        input_config_gj = os.path.join(current_dir, "../..", "input-gj.ini")
        shutil.copy(input_config_gj, input_config)

        persisted_settings = os.path.join(config_dir, 'PersistedSettings.json')
        if OS != "Windows":
            os.chmod(persisted_settings, 0o644)
        try:
            os.remove(game_config)
        except FileNotFoundError:
            pass
        config_settings = configparser.ConfigParser()
        config_settings.optionxform = str
        config_settings["General"] = {
            "WindowMode": "2",
            "Height": "768",
            "Width": "1024",
        }
        config_settings["Performance"] = {
            "ShadowQuality": "0",
            "FrameCapType": str(self.config.fps_type),
            "EnvironmentQuality": "0",
            "EffectsQuality": "0",
            "CharacterQuality": "0",
            "EnableGrassSwaying": "0",
            "EnableFXAA": "0",
        }
        with open(game_config, "w") as configfile:
            config_settings.write(configfile)
        with open(persisted_settings, 'r') as file:
            data = json.load(file)
        for file in data.get('files', []):
            for section in file.get('sections', []):
                if section.get('name') == 'ItemShop':
                    for setting in section.get('settings', []):
                        if setting.get('name') == 'CurrentTab':
                            setting['value'] = str(0)
                        if setting.get('name') == 'NativeOffsetX':
                            setting['value'] = str(0)
                        if setting.get('name') == 'NativeOffsetY':
                            setting['value'] = str(0)
                if section.get('name') == 'HUD':
                    for setting in section.get('settings', []):
                        if setting.get('name') == 'FlipMiniMap':
                            setting['value'] = str(0)
                        if setting.get('name') == 'MinimapScale':
                            setting['value'] = str(1.0000)
                        if setting.get('name') == 'ShopScale':
                            setting['value'] = str(0.4444)
                if section.get('name') == "General":
                    for setting in section.get('settings', []):
                        if setting.get('name') == 'EnableTargetedAttackMove':
                            setting['value'] = str(0)
        with open(persisted_settings, 'w') as file:
            json.dump(data, file, indent=4)
        if OS != "Windows":
            os.chmod(persisted_settings, 0o444)

    @staticmethod
    def print_ascii() -> None:
        """Prints some League ascii art."""
        print(
            """\n\n            
                    ──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
                    ───▄▄██▌█ BEEP BEEP
                    ▄▄▄▌▐██▌█ -15 LP DELIVERY
                    ███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                    ▀(⊙)▀▀▀▀▀▀▀(⊙)(⊙)▀▀▀▀▀▀▀▀▀▀(⊙)\n\n\t\t\t\tLoL Bot\n\n"""
        )
