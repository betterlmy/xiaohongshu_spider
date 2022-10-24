import threading
import time
from GUI import GUI_running

class MyThread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
    
    def run(self):
        X = 0
        while X<3:
            time.sleep(1)
            X +=1
            
if __name__ == "__main__":    
    t1 = MyThread("线程1")
    t1.start()
    print("我是Main")
    while True:
        print(t1.is_alive())
        time.sleep(0.5)
