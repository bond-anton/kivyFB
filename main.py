from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from front_panel_view import FrontPanelView


class MainApp(MDApp):

    theme_cls = ThemeManager()

    # def build(self):
    #     Window.bind(on_request_close=self.on_request_close)
    #     ui = BoxWidget()
    #     # Clock.schedule_interval(ui.update, 1/20)
    #
    #     self.sas = SAS(1, 'SAS', 100, ui=ui)
    #
    #     # Start new Threads
    #     self.sas.start()
    #
    #     return ui
    #
    # def on_request_close(self, *args):
    #     self.sas.exit_flag = True
    #     while not self.sas.stopped:
    #         time.sleep(1)
    #     self.stop()
    #     return True


if __name__ == "__main__":
    MainApp().run()
