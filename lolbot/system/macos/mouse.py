"""
This module provides functions to handle mouse clicks and movement on macOS.

On macOS, pyautogui functions as expected.
"""
from time import sleep

import pyautogui

pyautogui.FAILSAFE = False

def left_click(wait = .2):
    pyautogui.leftClick()
    sleep(wait)

def left_db_click(wait=.2):
    pyautogui.doubleClick()
    sleep(wait)

def right_click(wait = .2):
    pyautogui.rightClick()
    sleep(wait)

def move(coords: tuple, wait = .2):
    pyautogui.moveTo(coords)
    sleep(wait)

def move_and_click(coords: tuple, wait = .2):
    pyautogui.moveTo(coords)
    sleep(.2)
    pyautogui.leftClick()
    sleep(wait)