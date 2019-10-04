#!/encoding=utf-8
# ================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: my_thread.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-07-24
#   describe:
# ================================================================


import threading
import time

exitFlag = 0

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print_time(self.name, self.counter, 5)

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            (threading.Thread).exit()
        time.sleep(delay)
        counter -= 1

# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启线程
thread1.start()
thread2.start()

