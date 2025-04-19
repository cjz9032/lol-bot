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
    try:
        hwnd = FindWindow(None, window_title)
        if hwnd:
            SetForegroundWindow(hwnd)
    except Exception as e:
        pass

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

def convert_ratio_abs(ratio: tuple, win_x, win_y,win_l,win_h):
    updated_x = ((win_l - win_x) * ratio[0]) + win_x
    updated_y = ((win_h - win_y) * ratio[1]) + win_y
    return updated_x, updated_y



import win32gui

def get_pixel_color(x, y):
    hdc = win32gui.GetDC(0)  # 获取整个屏幕的设备上下文
    color = win32gui.GetPixel(hdc, x, y)  # 获取指定点的颜色
    win32gui.ReleaseDC(0, hdc)  # 释放设备上下文
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF

def is_color_close(color1, color2, tolerance=0.1):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return (abs(r1 - r2) <= tolerance * 255 and
            abs(g1 - g2) <= tolerance * 255 and
            abs(b1 - b2) <= tolerance * 255)

def is_color_close_by_xy(xy:tuple):
    target_color = (1, 13, 7)  # #010D07的RGB值
    pixel_color = get_pixel_color(int(xy[0]),int(xy[1]))
    return is_color_close(pixel_color, target_color)