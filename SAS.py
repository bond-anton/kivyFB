import threading
import time


class SAS (threading.Thread):

    def __init__(self, thread_id, name, counter, ui=None):
        threading.Thread.__init__(self)
        self.exit_flag = False
        self.stopped = False
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.ui = ui

    def run(self):
        time.sleep(5)
        print('Starting ' + self.name)
        self.stopped = False
        self.print_time(1)
        print('Exiting ' + self.name)

    def print_time(self, delay):
        while self.counter:
            if self.exit_flag:
                self.stopped = True
                break
            time.sleep(delay)
            print('%i) %s: %s' % (self.counter, self.name, time.ctime(time.time())))
            try:
                self.ui.update(0.2)
            except AttributeError:
                pass
            self.counter -= 1


if __name__ == "__main__":
    # Create new threads
    thread1 = SAS(1, 'Thread-1', 10)
    thread2 = SAS(2, 'Thread-2', 20)

    # Start new Threads
    thread1.start()
    thread2.start()
