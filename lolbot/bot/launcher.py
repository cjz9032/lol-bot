"""
Handles launching League of Legends and logging into an account.
"""
import logging
from time import sleep
from lolbot.system import cmd, keys, mouse, window, OS
from lolbot.lcu.league_client import LeagueClient, LCUError
import subprocess
import os
from lolbot.common import config

log = logging.getLogger(__name__)

# def left_click(ratio: tuple) -> None:
#     coords = window.convert_ratio(ratio, window.TX_LOGIN_WINDOW)
#     mouse.move(coords)
#     mouse.left_click()
#     sleep(0.6)


class LaunchError(Exception):
    """Indicates that League could not be opened."""
    pass

class Launcher:
    """Handles launching the League of Legends client and logging in"""

    def __init__(self):
        self.api = LeagueClient()
        self.username = ''
        self.password = ''
        self.attempts = 0
        self.riotAttemps = 0
        self.success = False
        self.config = config.load_config()

    def launch_league(self, username: str = '', password: str = ''):
        self.username = username
        self.password = password
        for i in range(3):
            self.launch_sequence()
            if self.success:
                return
        raise LaunchError("Could not open League. Ensure there are no pending updates.")

    def launchMac(self):
        cmd.run(cmd.LAUNCH_SPEEED)
        sleep(6)
        coords = window.convert_ratio((0.35,0.5), window.SPEED_WINDOW)
        mouse.move(coords)
        mouse.left_click()
        sleep(10)
        cmd.run(cmd.LAUNCH_CLIENT)
        sleep(50)

    def launchWindows(self):
        # prepare QQ
        # log.info("qq")
        # subprocess.Popen("C:\Program Files\Tencent\QQNT\QQ.exe", shell=True)
        # sleep(6)
        # keys.press_and_release('enter')
        # login_exe = os.path.join(self.config.windows_install_dir, '../TCLS/client.exe')
        # subprocess.Popen(login_exe, shell=True)
        # sleep(20)

        # window.bring_to_front(window.TX_LOGIN_WINDOW)
        # todo improve check
        # # rat = (arr)=>copy(`(${(arr[0]/1280).toFixed(4)}, ${(arr[1]/768).toFixed(4)})`)

        # left_click((0.8672, 0.4245))
        # sleep(2)
        # left_click((0.8969, 0.7969))
        # sleep(2)
        # left_click((0.8945, 0.7292))
        # sleep(2)
        # left_click((0.7141, 0.8138))
        # sleep(10)
        # cmd.run(cmd.CLOSE_QQ)
        # sleep(30)

        # wegame tray
        sleep(10)
        mouse.move((1117,938))
        mouse.left_db_click()
        sleep(5)

        # go
        window.bring_to_front(window.WG_LOGIN_WINDOW)
        mouse.move((1155,830)) # something does not work
        # coords = window.convert_ratio((0.96,0.96), window.WG_LOGIN_WINDOW)
        # mouse.move(coords)

        sleep(1)
        mouse.left_db_click()
        sleep(1)
        mouse.left_db_click()
        sleep(40)


    def launch_sequence(self):
        self.api.update_auth()

        # League is Running
        if cmd.run(cmd.IS_CLIENT_RUNNING):
            if self.attempts == 0:
                log.warning("League opened with prior login")
            else:
                log.info("Launch success")
                sleep(30)
            self.success = True

        # Riot Client is opened and Logged In
        elif cmd.run(cmd.IS_LAUNCHER_RUNNING) and self.api.access_token_exists():
            if self.attempts == 0:
                log.warning("Riot Client has previous login")
            else:
                log.info("Login Successful")
            try:
                log.info("Launching League from Client")
                self.riotAttemps += 1
                if self.riotAttemps == 3:
                    raise LaunchError("Max launch_league_from_rc from Riot Client attempts exceeded")
                self.api.launch_league_from_rc()
              
                sleep(30)
            except LCUError:
                pass
            return

        # Riot Client is opened and Not Logged In
        elif cmd.run(cmd.IS_LAUNCHER_RUNNING):
            if self.attempts == 3:
                raise LaunchError("Max login attempts exceeded. Check username and password")
            elif self.username == "" or self.password == "":
                raise LaunchError("Username or Password not set")

            log.info("Riot Client opened. Logging in")
            self.attempts += 1
            # self.lcu.login(self.username, self.password)
            self.manual_login()
            sleep(30)
            self.api.update_auth()
            if not self.api.access_token_exists():
                log.warning("Login attempt failed")
                cmd.run(cmd.CLOSE_ALL)
                sleep(10)

        # Nothing is opened
        else:
            log.info("Launching League of Legends")
            if OS == "Windows":
                self.launchWindows()
            else:
                self.launchMac()

    def manual_login(self):
        """
        Sends keystrokes into username and password fields. Only use if
        Riot Client lcu login does not work.
        """
        log.info('Manually logging into Riot Client')
        keys.write(self.username)
        sleep(.5)
        keys.press_and_release('tab')
        sleep(.5)
        keys.write(self.password)
        sleep(.5)
        keys.press_and_release('enter')
        sleep(1)

    def verify_account(self) -> bool:
        """Checks if account username match the account that is currently logged in."""
        log.info("Verifying logged-in account credentials")
        try:
            if self.username == self.api.get_summoner_name():
                log.info("Account Verified")
                return True
            else:
                log.warning("Accounts do not match!")
                return False
        except LCUError:
            log.warning("Could not get account information")
            return False
