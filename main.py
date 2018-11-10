#   Main.py
#   Will do more in the future
#   For now it calls WebData
from webdata import *
from random import randrange
from pprint import pprint
#   Kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.name = 'screen_main'

        self.base_layout = FloatLayout()
        self.add_widget(self.base_layout)
        scroll = RecycleView(size = (400, 400), size_hint = (None, None), center = Window.center)
        scroll.background = (1, 1, 1)
        self.base_layout.add_widget(scroll)
        scroll_box = BoxLayout(orientation='vertical', spacing = 2, padding = 10, size_hint_y = None)
        scroll_box.bind(minimum_height=scroll_box.setter('height'))
        scroll.add_widget(scroll_box)

        self.load_data()

        for key, item in list(self.data.items()) :
            l = Button(text = item['name'], size = (400, 30), size_hint = (1, None))
            scroll_box.add_widget(l)


    def load_data(self):
        self.data = get_data()
        save_data(self.data)
        print('Data Loaded')


class Main(App):
    def build(self):
        menu = MenuScreen()
        self.screenmanager = ScreenManager()
        self.screenmanager.add_widget(menu)
        self.screenmanager.current = menu.name
        return self.screenmanager

if (__name__ == '__main__'):
    Main().run()