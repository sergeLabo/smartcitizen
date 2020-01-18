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
from math import sin

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot

from smartcitizen_requests import SmartCitizenRequests

class MyGraph(Widget):

    pass


class Screen2(Screen):

    graph = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print([type(widget) for widget in self.walk(loopback=True)])

        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        # #self.ids.graph.add_plot(plot)


class Screen1(Screen):
    blanche = ObjectProperty(None)
    btns_text = ListProperty(["Smart Citizen"]*16)
    labels_text = ListProperty(["Capteur"]*16)
    owner_titre = StringProperty("")
    owner_detail = StringProperty("")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    """
    Utilisation de SmartCitizenRequests
    url = "http://api.smartcitizen.me/v0/devices/"
    device_nbr = 9525
    scr = SmartCitizenRequests(url, device_nbr)
    resp = scr.get_resp_dict(scr.instant_url)

    id_ = 55
    rollup = 4
    from_ = "2020-01-01"
    to_ = "2020-01-15"
    histo_url = scr.get_histo_url(id_, rollup, from_, to_)
    resp = scr.get_resp_dict(histo_url)
    histo = scr.get_histo(resp)
    [   ['2020-01-14T20:00:35Z', 18.709495798319324],
        ['2020-01-14T16:00:32Z', 18.996260504201675],
        .....
    """

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        # Permet d'appeler les attributs de app créé dans SmartCitizenApp
        self.app = app

        self.url = self.app.config.get('url', 'url')
        self.device_nbr = self.app.config.get('url', 'kit')

        # premier appel au lancement
        Clock.schedule_once(self.update)


        # Appel tous les 10 secondes
        Clock.schedule_interval(self.update, 10)

    def get_request_url(self):
        """url ne doit pas se terminer par /
        device est devices ou kits, pas de /
        device_nbr entre 0 et 100000, int
        A combiner avec la saisie des options !
        """
        # TODO pas utilisé, à faire
        if "http://api.smartcitizen.me" not in self.url:
            self.url = None

        if self.url:
            if self.url[-1] == "/":
                self.url = self.url[:-1]

        if "/" in self.device:
            self.device.replace("/", "")
        if self.device not in ["devices", "kits"]:
            self.device = None

        self.device_nbr = int(self.device_nbr)
        if self.device_nbr < 0: self.device_nbr= None
        if self.device_nbr > 20000: self.device_nbr= None

        if self.url and self.device and self.device_nbr:
            request_url = self.url + "/"\
                          + self.device + "/"\
                          + str(self.device_nbr)
        else:
            request_url = None

        print("Adresse des requêtes: {}".format(request_url))

        return request_url

    def update(self, dt):
        self.get_and_apply_instant_values()

    def get_and_apply_instant_values(self):
        """
        owner
        ('la labomedia', 'https://labomedia.org', 'Orléans', 'France')

        sensors
        description                      unit   value   id
        ['Digital Ambient Light Sensor', 'Lux', 31.79, 14],
        ['Custom Circuit', '%', -1.0, 10],
        ....

        kit
        'Smart Citizen Kit 2.1 with Urban Sensor Board'

        data
         exposure    alt   latitude           longitude
        ('outdoor', None, 47.9006640998651, 1.91683530807495)
        """

        scr = SmartCitizenRequests(self.url, self.device_nbr)
        resp = scr.get_resp_dict(scr.instant_url)

        # Détail du owner
        owner = scr.get_owner(resp)
        kit = scr.get_kit(resp)
        data = scr.get_data(resp)
        self.apply_owner(owner, kit, data)

        # Les valeurs de tous les capteurs
        sensors = scr.get_sensors(resp)
        self.apply_sensors(sensors)

    def apply_sensors(self, sensors):

        first_screen = self.ids.sm.get_screen("first")

        # 2*16 Cases vides
        first_screen.btns_text = [""]*16
        first_screen.labels_text = [""]*16

        # Ecrasement par nouvelles valeurs
        if sensors:
            x = min(len(sensors), 16)
            for d in range(x):
                description = textwrap.fill(sensors[d][0], 30)
                first_screen.btns_text[d] = description
                first_screen.labels_text[d] = str(round(sensors[d][2], 2))\
                                              + " "\
                                              + sensors[d][1]

    def apply_owner(self, owner, kit, data):

        first_screen = self.ids.sm.get_screen("first")

        # Reset
        first_screen.owner_titre = ""

        if owner[0]:
            first_screen.owner_titre = owner[0]
        else:
            first_screen.owner_titre = "Owner inconnu"

        if owner[1]:
            first_screen.owner_titre += "\n" + owner[1]

        # Reset
        first_screen.owner_detail = ""

        if kit:
            first_screen.owner_detail = kit

        if data:
            if data[0] == None: data[0] = ""
            if data[1] == None: data[1] = ""
            if data[2] == None: data[2] = ""
            if data[3] == None: data[3] = ""

            # exposure  alt  latitude  longitude
            first_screen.owner_detail += "Exposition" + str(data[0]) +\
                                         "Altitude" + str(data[1]) +\
                                         "Latitude" + str(data[2]) +\
                                         "Longitude" + str(data[3])


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
