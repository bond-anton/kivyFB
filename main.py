import numpy as np
from kivy.app import App

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty

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
    buffer_size_x = NumericProperty(800)
    buffer_size_y = NumericProperty(600)
    buffer_size = ReferenceListProperty(buffer_size_x, buffer_size_y)
    texture = ObjectProperty(None, allownone=True)
    data_texture = ObjectProperty(None, allownone=True)
    viewport = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(FboTest, self).__init__(**kwargs)
        # self.canvas = Canvas()
        print(self.buffer_size_x)
        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle()
            self.fbo.add_reload_observer(self.populate_fbo)

        self.data_texture = Texture.create(size=(self.buffer_size_x, self.buffer_size_y), colorfmt='luminance', bufferfmt='float', mipmap=True)
        self.data_texture.min_filter = 'nearest'
        self.data_texture.mag_filter = 'nearest'

        buffer_size = int(self.buffer_size_x * self.buffer_size_y)
        self.buffer = np.random.random(size=buffer_size).astype('float32')

        self.update_data_texture()

        # and load the data now.
        self.populate_fbo(self.fbo)

        self.texture = self.fbo.texture


    def gen_buffer(self):
        buffer_size = int(self.buffer_size_x * self.buffer_size_y)
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
