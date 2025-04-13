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
                keyboard.press(KeyCode.from_vk(0x12))
                keyboard.release(KeyCode.from_vk(0x12))
        case '2':
                keyboard.press(KeyCode.from_vk(0x13))
                keyboard.release(KeyCode.from_vk(0x13))
        case '3':
                keyboard.press(KeyCode.from_vk(0x14))
                keyboard.release(KeyCode.from_vk(0x14))
        case '4':
                keyboard.press(KeyCode.from_vk(0x15))
                keyboard.release(KeyCode.from_vk(0x15))
        case '5':
                keyboard.press(KeyCode.from_vk(0x17))
                keyboard.release(KeyCode.from_vk(0x17))
        case '6':
                keyboard.press(KeyCode.from_vk(0x16))
                keyboard.release(KeyCode.from_vk(0x16))
        case '7':
                keyboard.press(KeyCode.from_vk(0x1A))
                keyboard.release(KeyCode.from_vk(0x1A))
        case 'g':
                keyboard.press(KeyCode.from_vk(0x05))
                keyboard.release(KeyCode.from_vk(0x05))
        case 'v':
                keyboard.press(KeyCode.from_vk(0x09))
                keyboard.release(KeyCode.from_vk(0x09))
        case 'u':
                keyboard.press(KeyCode.from_vk(0x20))
                keyboard.release(KeyCode.from_vk(0x20))
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