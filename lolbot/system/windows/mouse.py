"""
This module provides functions to handle mouse clicks and movement on Windows.
On Windows, pyautogui mouse clicks do not work correctly. Need mouse package.
"""
from time import sleep

import mouse
import pyautogui

pyautogui.FAILSAFE = False

def left_click(wait=.2):
    mouse.click()
    sleep(wait)

def left_db_click(wait=.2):
    mouse.double_click()
    sleep(wait)

def right_click(wait=.2):
    mouse.right_click()
    sleep(wait)

def move(coords: tuple, wait=.2):
    pyautogui.moveTo(coords)
    sleep(wait)

def move_and_click(coords: tuple, wait=.2):
    pyautogui.moveTo(coords)
    sleep(.2)
    mouse.click()
    sleep(wait)
