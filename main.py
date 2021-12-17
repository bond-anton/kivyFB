import numpy as np
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
    viewport = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(FboTest, self).__init__(**kwargs)
        self.init_buffer()

        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle()
            self.fbo.add_reload_observer(self.populate_fbo)

        self.update_data_texture()
        self.populate_fbo(self.fbo)

        self.texture = self.fbo.texture

    def on_min_buffer_size_x(self, instance, value):
        pass

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
        self.update_viewport()

    def on_aspect_ratio(self, instance, value):
        x, y = self.apply_aspect_ratio(self.buffer_size)
        print('New aspect ratio is', value, 'actual aspect ratio is', x / y)
        if not [x, y] == value:
            self.buffer_size = [x, y]

    def gen_buffer(self):
        buffer_size = int(self.buffer_size[0] * self.buffer_size[1])
        self.buffer = np.random.random(size=buffer_size).astype('float32')
        self.update_data_texture()
        self.update_viewport()

    def update_data_texture(self):
        try:
            self.data_texture.blit_buffer(self.buffer, colorfmt='luminance', bufferfmt='float')
        except IndexError:
            pass

    def update_viewport(self):
        self.viewport.texture = self.data_texture

    def populate_fbo(self, fbo):
        with fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            Color(1, 1, 1, 1)
            self.viewport = Rectangle(size=self.size, pos=(0, 0), texture=self.data_texture)

    def on_size(self, instance, value):
        if 0 in value:
            pass
        else:
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

    def update(self, dt):
        self.viewport.gen_buffer()


class FBViewApp(App):
    def build(self):
        ui = BoxWidget()
        Clock.schedule_interval(ui.update, 0.01)
        return ui


if __name__ == "__main__":
    FBViewApp().run()
