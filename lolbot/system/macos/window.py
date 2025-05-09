from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

GAME_WINDOW = 'League Of Legends'
CLIENT_WINDOW = 'League of Legends'
SPEED_WINDOW = 'UU 加速器'


class WindowNotFound(Exception):
    pass


def check_window_exists(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            bounds = window.get('kCGWindowBounds', {})
            if bounds.get('X') > 0 and bounds.get('Y') > 0:
                return True
    raise WindowNotFound


def get_window_size(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            bounds = window.get('kCGWindowBounds', {})
            x = bounds.get('X')
            y = bounds.get('Y')
            l = bounds.get('Width')
            h = bounds.get('Height')
            if x != 0 and y != 0:
                return x, y, l, h
    raise WindowNotFound


def convert_ratio(ratio: tuple, window_name: str):
    x, y, l, h = get_window_size(window_name)
    updated_x = (l * ratio[0]) + x
    updated_y = (h * ratio[1]) + y
    return updated_x, updated_y

def convert_ratio_abs(ratio: tuple, win_x, win_y,win_l,win_h):
    updated_x = (win_l * ratio[0]) + win_x
    updated_y = (win_h * ratio[1]) + win_y
    return updated_x, updated_y