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


__version__ = '0.01'

import os, sys

import kivy
kivy.require('1.11.1')

# Pour mon PC
if sys.platform == 'linux':
    from kivy.core.window import Window
    # Pour simuler l'écran de mon tél fait 1280*720
    k = 0.8
    WS = (int(720*k), int(1280*k))
    Window.size = WS

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock

from smartcitizen_requests import SmartCitizenRequests

class Screen2(Screen):
    pass

class Screen1(Screen):
    pass

class MainScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

class SmartCitizen(BoxLayout):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        # Permet d'appeler les attributs de app
        self.app = app

        self.font_size = 10
        self.font_size_sp = "10sp"
        self.app.text = "toto\n"*10

        self.url = "http://api.smartcitizen.me/v0/"
        self.device = "devices"
        self.device_nbr = str(9565)
        self.data = None

        self.event = Clock.schedule_interval(self.update, 10)

    def update(self, dt):
        scr = SmartCitizenRequests(self.url, self.device, self.device_nbr)
        resp_dict = scr.get_one_request()
        scr.get_data(resp_dict)
        self.data = scr.data

        self.app.text = self.format_data()

    def format_data(self):

        text = ""
        for d in self.data:
            text = text + d[0] + "  " + str(d[2]) + " " + d[1] + "\n\n"
        print(text)
        return text

class SmartCitizenApp(App):

    text = StringProperty("toto\n"*10)
    font_size_sp = StringProperty("10sp")

    def build(self):
        return SmartCitizen(self)

    def on_start(self):

        pass

    def build_config(self, config):
        config.setdefaults("font", {"font_size": 20, "unit": "sp" })

    def build_settings(self, settings):
        data = '''[ { "type": "title", "title":"Taille des textes"},

                    { "type": "numeric",
                      "title": "Taille des textes",
                      "desc": "De 10 à 40",
                      "section": "font",
                      "key": "font_size"},

                    { "type": "string",
                      "title": "Taille de la police en:",
                      "desc": "sp ou dp",
                      "section": "font",
                      "key": "unit"}
                      ]'''
        settings.add_json_panel('Configuration de SmartCitizen', self.config, data=data)

    def on_config_change(self, config, section, key, value):

        if config is self.config:  # du joli python rigoureux
            token = (section, key)

            # Font size
            if token == ('font', 'font_size'):
                value = int(value)
                if value < 0: value = 0
                if value > 40: value = 40
                print("Nouvelle taille de police:", value)
                self.root.format_data()

if __name__ == '__main__':
    SmartCitizenApp().run()
