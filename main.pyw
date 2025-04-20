"""
Where bot execution starts
"""
import sys
import io
import requests
from time import sleep
import socket
# 强制标准输出使用 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lolbot.view.main_window import MainWindow

# 设置超时时间（秒）
timeout = 5.0


def get_host_ip():
    hostname = socket.gethostname()  # 获取本机主机名
    ip = socket.gethostbyname(hostname)  # 根据主机名获取 IP 地址
    return ip

if __name__ == '__main__':
    try:
        # 创建一个会话对象，用于保持会话
        session = requests.Session()

        # 第一个请求
        url1 = "http://192.168.0.1/goform/goform_set_cmd_process"
        headers1 = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "pragma": "no-cache",
            "x-requested-with": "XMLHttpRequest",
            "referer": "http://192.168.0.1/index.html"
        }
        data1 = "goformId=LOGIN&password=YWRtaW4%3D"
        response1 = session.post(url1, headers=headers1, data=data1, timeout=timeout)

        # 第二个请求
        url2 = "http://192.168.0.1/goform/goform_set_cmd_process"
        headers2 = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "pragma": "no-cache",
            "x-requested-with": "XMLHttpRequest",
            "referer": "http://192.168.0.1/index.html"
        }
        data2 = "goformId=DNS_SETTING&dns_manual_enable=1&dhcpDns=223.5.5.5"
        response2 = session.post(url2, headers=headers2, data=data2 , timeout=timeout)

        # 打印响应内容
        print("第一个请求的响应内容：")
        print(response1.text)
        print("第二个请求的响应内容：")
        print(response2.text)
    except Exception as e:
        print(f"Failed to dns: {e}")
        try:
            requests.get(f"https://www.pushplus.plus/send?token=513c57c01734486086a393226c97c55d&title=dns&content={e}&template=txt")
        except Exception as e:
            print(f"Failed to dns2: {e}")



    try:
        ip = get_host_ip()
        requests.get(f"https://www.pushplus.plus/send?token=513c57c01734486086a393226c97c55d&title=ip&content={ip}&template=txt")
    except Exception as e:
        print(f"Failed to ip: {e}")
        pass

    sleep(3)
    gui: MainWindow = MainWindow()
    gui.show()
