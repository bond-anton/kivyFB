from datetime import datetime, timedelta

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.app import MDApp

from front_panel_view import FrontPanelView
from status_bar import StatusBar


class DisplayBox(BoxLayout):
    pass


class MainApp(MDApp):

    def build(self):
        self.now = datetime.now()
        ui = DisplayBox()
        Clock.schedule_interval(self.update_clock, 1)
        return ui

    def on_start(self):
        self.theme_cls.primary_palette = 'BlueGray'

    def update_clock(self, *args):
        # self.now = self.now + timedelta(seconds=1)
        self.now = datetime.now()
        self.root.ids.status_bar.ids.time_label.text = self.now.strftime('%H:%M:%S')

    def set_screen(self, screen_name):
        self.root.ids.front_panel_view.ids.screen_manager.current = screen_name


if __name__ == "__main__":
    MainApp().run()
