import threading
import time


exit_flag = 0


class SAS (threading.Thread):

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        print('Starting ' + self.name)
        print_time(self.name, self.counter, 1)
        print('Exiting ' + self.name)


def print_time(thread_name, counter, delay):
    while counter:
        if exit_flag:
            break
        time.sleep(delay)
        print('%i) %s: %s' % (counter, thread_name, time.ctime(time.time())))
        counter -= 1


if __name__ == "__main__":
    # Create new threads
    thread1 = SAS(1, 'Thread-1', 10)
    thread2 = SAS(2, 'Thread-2', 20)

    # Start new Threads
    thread1.start()
    thread2.start()
