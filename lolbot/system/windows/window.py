"""
Utility functions for determining if a window exists.
"""

from win32gui import FindWindow, GetWindowRect, SetForegroundWindow

GAME_WINDOW = "League of Legends (TM) Client"
CLIENT_WINDOW = "League of Legends"
TX_LOGIN_WINDOW = "英雄联盟登录程序"
WG_LOGIN_WINDOW = "WeGame"


class WindowNotFound(Exception):
    pass


def check_window_exists(window_name: str):
    if FindWindow(None, window_name) == 0:
        raise WindowNotFound
    return True

def bring_to_front(window_title):
    hwnd = FindWindow(None, window_title)
    if hwnd:
        SetForegroundWindow(hwnd)

def get_window_size(window_name: str):
    """Gets the size of an open window"""
    window_handle = FindWindow(None, window_name)
    if window_handle == 0:
        raise WindowNotFound
    window_rect = GetWindowRect(window_handle)
    return window_rect[0], window_rect[1], window_rect[2], window_rect[3]


def convert_ratio(ratio: tuple, window_name: str):
    x, y, l, h = get_window_size(window_name)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    return updated_x, updated_y
