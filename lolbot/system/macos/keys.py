"""
This module provides functions to handle keyboard actions on macOS.
"""

from pynput.keyboard import Key, Controller, KeyCode

keyboard = Controller()

def press_and_release(key: str):
    match key:
        case 'esc' :
            keyboard.press(Key.esc)
            keyboard.release(Key.esc)
        case 'ctrl+r':
            with keyboard.pressed(Key.ctrl):
                keyboard.press('r')
                keyboard.release('r')
        case 'ctrl+q':
            with keyboard.pressed(Key.ctrl):
                keyboard.press('q')
                keyboard.release('q')
        case 'ctrl+w':
            with keyboard.pressed(Key.ctrl):
                keyboard.press('w')
                keyboard.release('w')
        case 'ctrl+e':
            with keyboard.pressed(Key.ctrl):
                keyboard.press('e')
                keyboard.release('e')
        case '1':
                keyboard.press(KeyCode.from_vk(18))
                keyboard.release(KeyCode.from_vk(18))
        case '2':
                keyboard.press(KeyCode.from_vk(19))
                keyboard.release(KeyCode.from_vk(19))
        case '3':
                keyboard.press(KeyCode.from_vk(20))
                keyboard.release(KeyCode.from_vk(20))
        case '4':
                keyboard.press(KeyCode.from_vk(21))
                keyboard.release(KeyCode.from_vk(21))
        case '5':
                keyboard.press(KeyCode.from_vk(22))
                keyboard.release(KeyCode.from_vk(22))
        case '6':
                keyboard.press(KeyCode.from_vk(23))
                keyboard.release(KeyCode.from_vk(23))
        case '7':
                keyboard.press(KeyCode.from_vk(24))
                keyboard.release(KeyCode.from_vk(24))
        case 'tab':
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        case 'enter':
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        case _:
            keyboard.press(key)
            keyboard.release(key)

def key_down(key: str):
    keyboard.press(key)

def key_up(key: str):
    keyboard.release(key)

def write(text: str):
    keyboard.type(text)