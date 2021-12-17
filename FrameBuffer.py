import numpy as np
from collections import deque


class FrameBuffer(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = width * height

        self.framebuffer = deque([], maxlen=self.size)

        self.idx = 0
        self.data_ready = 0

    def put_datapoint(self, value):
        self.framebuffer.append(value)
        self.data_ready += 1
        if self.data_ready > self.size:
            self.idx = (self.idx + 1) % self.size
            self.data_ready = self.size

    def get_datapoint(self):
        if self.data_ready > 0:
            self.data_ready -= 1
            self.idx = (self.idx + 1) % self.size
            return self.framebuffer.popleft()
        return None

    def put_data(self, data):
        self.framebuffer.extend(data)
        self.data_ready += len(data)
        if self.data_ready > self.size:
            self.idx = (self.idx + self.data_ready % self.size) % self.size
            self.data_ready = self.size

    def get_data(self):
        i = self.idx
        if self.data_ready > 0:
            data = np.array(self.framebuffer)
            self.framebuffer.clear()
            self.idx = (self.idx + self.data_ready) % self.size
            self.data_ready = 0
            return i, data
        return i, None
