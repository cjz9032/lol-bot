
import multiprocessing as mp
from pynput.keyboard import Listener, Key

 

class BG:

    def __init__(self) -> None:
        pass
    # def on_press(self, key):
    #     try:
    #         self.event_queue.put(f"按键被按下: {key.char}")
    #     except AttributeError:
    #         self.event_queue.put(f"特殊按键被按下: {key}")

    def on_release(self, key):
        self.event_queue.put(f"按键被释放: {key}")
        if key == Key.esc:  # 按下 Esc 键退出
            self.event_queue.put(f"按键被释放2: {key}")
            self.event_queue.put("stop")  # 发送停止信号
            return False  # 停止监听器
        
    def run(self, event_queue: mp.Queue):
        self.event_queue = event_queue
        with Listener(on_release=self.on_release) as listener:
            listener.join()
       
        