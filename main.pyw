"""
Where bot execution starts
"""
import sys
import io

# 强制标准输出使用 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lolbot.view.main_window import MainWindow

if __name__ == '__main__':
    gui: MainWindow = MainWindow()
    gui.show()
