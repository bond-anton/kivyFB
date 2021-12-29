import math as m
import numpy as np
import time

from kivy.app import App

from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty, ListProperty
from kivy.properties import ObjectProperty

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Fbo
from kivy.graphics import Color, Canvas, ClearBuffers, ClearColor
from kivy.graphics import Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from statistics import mean, stdev, StatisticsError
from FrameBuffer import FrameBuffer
from SAS import SAS


def coerce_power_of_two(value):
    if value == 0:
        value = 1
    n = int(round(m.log2(abs(value))))
    if n < 0:
        n = 0
    return int(m.copysign(2 ** n, value))


class FboTest(Widget):

    power_of_two_only = BooleanProperty(True)
    keep_aspect_ratio = BooleanProperty(True)
    aspect_ratio = NumericProperty(16 / 9)

    min_buffer_size_x = NumericProperty(1)     # 2**0
    min_buffer_size_y = NumericProperty(1)     # 2**0
    max_buffer_size_x = NumericProperty(8192)  # 2**12
    max_buffer_size_y = NumericProperty(8192)  # 2**12

    buffer_size = ListProperty([640, 480])
    buffer = None

    texture = ObjectProperty(None, allownone=True)
    data_texture = None
    viewer = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(FboTest, self).__init__(**kwargs)

        self.fps_meter = FrameBuffer(100, 1)
        self.last_frame = time.time()

        if self.power_of_two_only:
            self.min_buffer_size_x = coerce_power_of_two(self.min_buffer_size_x)
            self.max_buffer_size_x = coerce_power_of_two(self.max_buffer_size_x)
            self.min_buffer_size_y = coerce_power_of_two(self.min_buffer_size_y)
            self.max_buffer_size_y = coerce_power_of_two(self.max_buffer_size_y)
        self.init_buffer()

        self.idx = 0

        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle()
            self.fbo.add_reload_observer(self.populate_fbo)

        self.update_data_texture()

        self.viewer_size = self.size
        self.viewer_pos = [0, 0]

        self.populate_fbo(self.fbo)

        self.texture = self.fbo.texture

    def on_min_buffer_size_x(self, instance, value):
        if self.power_of_two_only:
            a = coerce_power_of_two(value)
        else:
            a = int(round(value))
        if a < 0:
            a = 1
        if self.min_buffer_size_x == a:
            pass
        else:
            if self.max_buffer_size_x < a:
                self.min_buffer_size_x = self.max_buffer_size_x
                self.max_buffer_size_x = a
            else:
                self.min_buffer_size_x = a
        print('min X', self.min_buffer_size_x, self.max_buffer_size_x)

    def on_min_buffer_size_y(self, instance, value):
        if self.power_of_two_only:
            a = coerce_power_of_two(value)
        else:
            a = int(round(value))
        if a < 0:
            a = 1
        if self.min_buffer_size_y == a:
            pass
        else:
            if self.max_buffer_size_y < a:
                self.min_buffer_size_y = self.max_buffer_size_y
                self.max_buffer_size_y = a
            else:
                self.min_buffer_size_y = a
        print('min Y', self.min_buffer_size_y, self.max_buffer_size_y)

    def on_max_buffer_size_x(self, instance, value):
        if self.power_of_two_only:
            a = coerce_power_of_two(value)
        else:
            a = int(round(value))
        if a < 0:
            a = 1
        if self.max_buffer_size_x == a:
            pass
        else:
            if self.min_buffer_size_x > a:
                self.max_buffer_size_x = self.min_buffer_size_x
                self.min_buffer_size_x = a
            else:
                self.max_buffer_size_x = a
        print('max X', self.min_buffer_size_x, self.max_buffer_size_x)

    def on_max_buffer_size_y(self, instance, value):
        if self.power_of_two_only:
            a = coerce_power_of_two(value)
        else:
            a = int(round(value))
        if a < 0:
            a = 1
        if self.max_buffer_size_y == a:
            pass
        else:
            if self.min_buffer_size_y > a:
                self.max_buffer_size_y = self.min_buffer_size_y
                self.min_buffer_size_y = a
            else:
                self.max_buffer_size_y = a
        print('max Y', self.min_buffer_size_y, self.max_buffer_size_y)

    def init_buffer(self):
        buffer_size = int(self.buffer_size[0] * self.buffer_size[1])
        self.buffer = np.zeros(buffer_size, dtype='float32')
        self.data_texture = Texture.create(size=(self.buffer_size[0], self.buffer_size[1]), colorfmt='luminance',
                                           bufferfmt='float', mipmap=True)
        self.data_texture.min_filter = 'nearest'
        self.data_texture.mag_filter = 'nearest'
        self.update_data_texture()

    def coerce_buffer_size(self, buffer_size):
        x, y = buffer_size
        if self.power_of_two_only:
            x = coerce_power_of_two(x)
            y = coerce_power_of_two(y)
        if x < self.min_buffer_size_x:
            x = self.min_buffer_size_x
        elif x > self.max_buffer_size_x:
            x = self.max_buffer_size_x
        if y < self.min_buffer_size_y:
            y = self.min_buffer_size_y
        elif y > self.max_buffer_size_y:
            y = self.max_buffer_size_y
        return x, y

    def apply_aspect_ratio(self, buffer_size):
        x, y = buffer_size
        if self.keep_aspect_ratio:
            if x / self.aspect_ratio > self.max_buffer_size_y:
                y = self.max_buffer_size_y
                x = int(y * self.aspect_ratio)
            else:
                y = int(x / self.aspect_ratio)
        else:
            self.aspect_ratio = x / y
        x, y = self.coerce_buffer_size([x, y])
        return x, y

    def on_buffer_size(self, instance, value):
        print('New buffer size is', value)
        x, y = self.coerce_buffer_size(value)
        x, y = self.apply_aspect_ratio([x, y])
        if not [x, y] == value:
            self.buffer_size = [x, y]
        self.init_buffer()
        self.update_viewer()

    def on_aspect_ratio(self, instance, value):
        x, y = self.apply_aspect_ratio(self.buffer_size)
        print('New aspect ratio is', value, 'actual aspect ratio is', x / y)
        if not [x, y] == self.buffer_size:
            self.buffer_size = [x, y]

    def gen_buffer(self):
        t0 = time.time()
        buffer_size = 1
        buffer_size = self.buffer_size[0]
        # self.buffer = np.random.random(size=self.buffer_size[0] * self.buffer_size[1]).astype('float32')
        self.buffer = np.random.random(size=buffer_size).astype('float32')
        # self.buffer = np.array([self.idx / (self.buffer_size[0] * self.buffer_size[1])], dtype='float32')
        i = int(self.idx % self.buffer_size[0])
        j = int(self.buffer_size[1] - self.idx // self.buffer_size[0] - 1)
        # self.buffer = np.array([i / self.buffer_size[0] + (self.buffer_size[1] - j - 1) / self.buffer_size[1]], dtype='float32')
        # self.idx += 1
        self.idx += buffer_size
        if self.idx == self.buffer_size[0] * self.buffer_size[1]:
            self.idx = 0
        t1 = time.time()
        # self.update_data_texture(size=(1, 1), pos=(i, j))
        self.update_data_texture(size=(buffer_size, 1), pos=(i, j))
        # self.update_data_texture()
        t2 = time.time()
        self.update_viewer()
        t3 = time.time()
        # print((t1-t0)*1000, (t2-t1)*1000, (t3-t2)*1000, (t3-t0)*1000)
        self.fps_meter.put_datapoint(1/(t3-self.last_frame))
        self.last_frame = t3
        # try:
            # print(mean(self.fps_meter.framebuffer), stdev(self.fps_meter.framebuffer))
            # print(self.fps_label)
            # self.fps_label.text = '%2.2f +- %2.2f fps' % (mean(self.fps_meter.framebuffer), stdev(self.fps_meter.framebuffer))
            # self.fps_label.texture_update()
        # except:
        #     pass

    def update_data_texture(self, size=None, pos=(0, 0)):
        if size is None:
            size = self.buffer_size
        try:
            self.data_texture.blit_buffer(self.buffer, size=size, pos=pos,
                                          colorfmt='luminance', bufferfmt='float')
        except IndexError:
            pass

    def update_viewer(self):
        self.viewer.texture = self.data_texture

    def populate_fbo(self, fbo):
        with fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            Color(1, 1, 1, 1)
            self.viewer = Rectangle(size=self.viewer_size, pos=self.viewer_pos, texture=self.data_texture)

    def on_size(self, instance, value):
        if 0 in value:
            pass
        else:
            vp_x, vp_y = value
            if self.keep_aspect_ratio:
                aspect_ratio_fb = self.buffer_size[0] / self.buffer_size[1]
                aspect_ratio_vp = value[0] / value[1]
                if aspect_ratio_fb > aspect_ratio_vp:
                    vp_y = value[0] / aspect_ratio_fb
                elif aspect_ratio_fb < aspect_ratio_vp:
                    vp_x = value[1] * aspect_ratio_fb
            self.viewer_size = [vp_x, vp_y]
            self.viewer_pos = [(value[0] - vp_x) / 2, (value[1] - vp_y) / 2]
            self.fbo.size = value
            self.texture = self.fbo.texture
            self.fbo_rect.size = value
            self.populate_fbo(self.fbo)

    def on_pos(self, instance, value):
        self.fbo_rect.pos = value

    def on_texture(self, instance, value):
        self.fbo_rect.texture = value


class BoxWidget(BoxLayout):
    viewport = ObjectProperty(None)
    fps_label = ObjectProperty(None)

    fps = 0
    d_fps = 0

    def update(self, dt):
        self.viewport.gen_buffer()
        try:
            self.fps = int(mean(self.viewport.fps_meter.framebuffer))
            self.d_fps = int(stdev(self.viewport.fps_meter.framebuffer))
            self.fps_label.text = '%i +- %i fps' % (self.fps, self.d_fps)
        except StatisticsError:
            pass


class FBViewApp(App):

    def build(self):
        ui = BoxWidget()
        Clock.schedule_interval(ui.update, 1/20)

        thread1 = SAS(1, 'Thread-1', 10)
        thread2 = SAS(2, 'Thread-2', 20)

        # Start new Threads
        thread1.start()
        thread2.start()

        return ui


if __name__ == "__main__":
    FBViewApp().run()
