from datetime import datetime, timedelta

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem


class DisplayBox(BoxLayout):
    pass


class MainApp(MDApp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.now = datetime.now()
        self.network = False
        self.serial_port_list = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6']
        self.serial_port_menu = MDDropdownMenu()

    def build(self):
        ui = DisplayBox()
        self.serial_port_menu = MDDropdownMenu(
            caller=ui.ids.front_panel_view.ids.connection_setup.ids.serial_port_dropdown,
            items=[
                {
                    'viewclass': 'OneLineListItem',
                    'text': serial_port,
                    'on_release': lambda x=serial_port: self.select_serial_port(x),
                } for serial_port in self.serial_port_list],
            #position='center',
            width_mult=5
        )
        Clock.schedule_interval(self.update_clock, 1)
        return ui

    def on_start(self):
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.theme_style = 'Light'
        self.root.ids.status_bar.ids.label_title.font_size = '10sp'
        self.root.ids.front_panel_view.ids.connection_setup.ids.serial_port_dropdown.set_item(self.serial_port_list[0])

    def update_clock(self, *args):
        self.now = datetime.now()
        self.root.ids.status_bar.title = self.now.strftime('%a %d %b %Y %H:%M:%S')

    def set_screen(self, screen_name):
        self.root.ids.front_panel_view.ids.screen_manager.current = screen_name

    def on_select_connection(self, checkbox, value):
        if value:
            if checkbox.name == 'network':
                print('network')
                self.network = True
            else:
                print('serial')
                self.network = False

    def select_serial_port(self, serial_port):
        print('Port selected:', serial_port)
        self.root.ids.front_panel_view.ids.connection_setup.ids.serial_port_dropdown.set_item(serial_port)
        self.serial_port_menu.dismiss()



if __name__ == "__main__":
    MainApp().run()
