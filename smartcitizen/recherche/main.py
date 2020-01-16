#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
# Copyright (C) La Labomedia January 2020
#
# This file is part of Smart Citizen.

# Smart Citizen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Smart Citizen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Smart Citizen.  If not, see <https://www.gnu.org/licenses/>.
#######################################################################


__version__ = '0.04'

import kivy
kivy.require('1.11.1')

# Pour mon PC
import sys
if sys.platform == 'linux':
    from kivy.core.window import Window
    # Pour simuler l'écran de mon tél qui fait 1280*720
    k = 0.8
    WS = (int(720*k), int(1280*k))
    Window.size = WS

import textwrap

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.button import Button

from smartcitizen_requests import SmartCitizenRequests


class Screen2(Screen):
    pass


class Sensor(BoxLayout):

    index = NumericProperty()
    text = StringProperty("toto")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("index", self.index)

class Screen1(Screen):
    blanche = ObjectProperty(None)
    btns_text = ListProperty(["Smart Citizen"]*16)
    labels_text = ListProperty(["Capteur"]*16)
    titre_text = StringProperty("Texte")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        some = self.ids.s0
        print([type(widget) for widget in some.walk(loopback=True)])
        some.text = "tata"


    def on_button_state(self, instance, value):
        """Call if button state change."""

        print(instance, value, instance.index)
        index = instance.index
        if value == 'down':
            value = int(index)
        else:
            value = 0


class MainScreen(Screen):
    pass


class ScreenManager(ScreenManager):
    pass


class SmartCitizen(BoxLayout):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        # Permet d'appeler les attributs de app créé dans SmartCitizenApp
        self.app = app

        self.url = "http://api.smartcitizen.me/v0/"
        self.device = "devices"
        self.device_nbr = self.app.config.get('kit', 'kit')
        print("Kit:", self.device_nbr)
        self.data = None
        self.owner = None

        # premier appel au lancement
        self.get_data()
        self.apply_data()
        self.apply_owner()

        # Appel tous les 10 secondes
        self.event = Clock.schedule_interval(self.update, 10)

    def update(self, dt):
        self.get_data()
        self.apply_data()
        self.apply_owner()

    def get_data(self):
        self.device_nbr = self.app.device_nbr
        print(self.device_nbr)
        scr = SmartCitizenRequests(self.url, self.device, self.device_nbr)
        scr.get_one_request()
        scr.get_data()
        self.data = scr.data
        self.owner = scr.owner

    def apply_data(self):

        first_screen = self.ids.sm.get_screen("first")

        # 2*16 Cases vides
        first_screen.btns_text = [""]*16
        first_screen.labels_text = [""]*16

        # Ecrasement par nouvelles valeurs
        x = min(len(self.data), 16)
        for d in range(x):
            description = textwrap.fill(self.data[d][0], 30)
            first_screen.btns_text[d] = description
            first_screen.labels_text[d] = str(self.data[d][2]) + " "\
                                          + self.data[d][1]

    def apply_owner(self):

        first_screen = self.ids.sm.get_screen("first")
        if self.owner[0] and self.owner[1]:
            first_screen.titre_text = self.owner[0] + "\n" + self.owner[1]
        else:
            first_screen.titre_text = "Kit inexistant"


class SmartCitizenApp(App):

    def build(self):
        self.device_nbr = self.config.get('kit', 'kit')
        return SmartCitizen(self)

    def on_start(self):
        pass

    def build_config(self, config):
        config.setdefaults("font", {"font_size": 20, "unit": "sp" })

        config.setdefaults("kit", {"kit": 9525 })

    def build_settings(self, settings):
        data = '''[ { "type": "title", "title":"Taille des textes"},

                    { "type": "numeric",
                      "title": "Taille des textes",
                      "desc": "De 10 à 40",
                      "section": "font",
                      "key": "font_size"},

                    { "type": "numeric",
                      "title": "Numéro du kit",
                      "desc": "0 à 20 000",
                      "section": "kit",
                      "key": "kit"}
                      ]'''

        settings.add_json_panel('Configuration de SmartCitizen', self.config, data=data)

    def on_config_change(self, config, section, key, value):

        if config is self.config:  # du joli python rigoureux
            token = (section, key)

            # Font size
            if token == ('kit', 'kit'):
                value = int(value)
                if value < 0: value = 0
                if value > 20000: value = 20000
                print("Nouveau kit:", value)
                self.config.set('kit', 'kit', value)
                # SmartCitizen viendra chercher cet attribut de cette class
                self.device_nbr = value

    def do_quit(self):
        SmartCitizenApp.get_running_app().stop()


if __name__ == '__main__':
    SmartCitizenApp().run()
