"""
Main window that displays all the tabs.
"""

import time

import dearpygui.dearpygui as dpg

from lolbot.view.bot_tab import BotTab
from lolbot.view.accounts_tab import AccountsTab
from lolbot.view.config_tab import ConfigTab
from lolbot.view.http_tab import HTTPTab
from lolbot.view.logs_tab import LogsTab
from lolbot.view.about_tab import AboutTab
from lolbot.lcu.league_client import LeagueClient
from lolbot.system import RESOLUTION, cmd, OS
from lolbot.common.config import ICON_PATH

CHECK_INTERNAL_MIN = 300

class MainWindow:

    def __init__(self) -> None:
        dpg.create_context()
        self.width = RESOLUTION[0]
        self.height = RESOLUTION[1]
        self.tab_bar = None
        self.api = LeagueClient()
        self.bot_tab = BotTab(self.api)
        self.accounts_tab = AccountsTab()
        self.config_tab = ConfigTab()
        self.https_tab = HTTPTab(self.api)
        self.logs_tab = LogsTab()
        self.about_tab = AboutTab()
        self.api.update_auth_timer()
        self.start_time = time.time()
        self.lastCheckBroken = time.time()

    def show(self) -> None:
        with dpg.window(label='', tag='primary window', width=self.width, height=self.height, no_move=True, no_resize=True, no_title_bar=True):
            with dpg.theme(tag="__hyperlinkTheme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])
            with dpg.tab_bar() as self.tab_bar:
                self.bot_tab.create_tab(self.tab_bar)
                self.accounts_tab.create_tab(self.tab_bar)
                self.config_tab.create_tab(self.tab_bar)
                self.https_tab.create_tab(self.tab_bar)
                self.logs_tab.create_tab(self.tab_bar)
                self.about_tab.create_tab(self.tab_bar)
        dpg.create_viewport(title='LoL Bot', width=self.width, height=self.height, small_icon=ICON_PATH, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('primary window', True)
        dpg.set_exit_callback(self.on_exit)
        panel_update_time = time.time()
        while dpg.is_dearpygui_running():
            current_time = time.time()
            if current_time - self.lastCheckBroken >= CHECK_INTERNAL_MIN:
                self.lastCheckBroken = current_time
                self.bot_tab.check_broken()
            if current_time - panel_update_time >= 0.3:
                self.bot_tab.update_bot_panel()
                self.bot_tab.update_info_panel()
                self.bot_tab.update_output_panel()
                panel_update_time = current_time
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    def on_exit(self):
        self.api.stop_timer()
        self.bot_tab.stop_bot()
