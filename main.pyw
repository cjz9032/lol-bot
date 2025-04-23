"""
Where bot execution starts
"""
import sys
import io
from time import sleep

# 强制标准输出使用 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from day import  isValidTimeForRiotWin
from lolbot.view.main_window import MainWindow

if __name__ == '__main__':
    while True:
        if isValidTimeForRiotWin():
            break
        else:
            sleep(60000)

    gui: MainWindow = MainWindow()
    gui.show()
