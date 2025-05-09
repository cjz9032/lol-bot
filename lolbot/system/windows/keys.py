"""
This module provides functions to handle keyboard actions on Windows.
The keyboard package works normally on Windows.
"""

import keyboard


def press_and_release(key: str):
    keyboard.press_and_release(key)


def key_down(key: str):
    keyboard.press(key)


def key_up(key: str):
    keyboard.release(key)

def key_self_press(key: str):
    keyboard.press('alt')
    press_and_release(key)
    keyboard.release('alt')

def write(text: str):
    keyboard.write(text, delay=.1)

