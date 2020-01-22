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
import datetime
# #from time import sleep

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.uix.popup import Popup

from smartcitizen_requests import SmartCitizenRequests


class MyGraph(Graph):
    """Documentation de kivy_garden.graph à
    https://kivy-garden.github.io/graph/flower.html

    Impossible d'ajouter la courbe à graph:
        d'où création de graph dans ce script.
    class non utilisée.
    """
    pass


class Screen2(Screen):

    graph_id = ObjectProperty()
    titre = StringProperty("Capteur")

    def __init__(self, **kwargs):
        """self.graph ne peut pas être initié ici, il doit être dans une autre
        méthode.
        # Pour initier le graph
        # #Clock.schedule_once(self.graph_init)
        """

        super().__init__(**kwargs)

        self.sensor_id = None
        self.unit = ""
        self.graph = None
        self.histo = []
        self.histo_data = (1, "2020-01-15", "2020-01-20")
        self.y_major = 1
        self.titre = "Capteur"

    def graph_init(self):
        """Initialisation de self.graph.
        plot initié avec 100 couples [(x, y), ...]
        """

        print("Initialisation du graph")

        # Si existe je détruits
        if self.graph:
            self.ids.graph_id.remove_widget(self.graph)
            print("self.graph détruit")

        # Récup de data dans Screen1
        first_screen = self.manager.get_screen("first")
        # ['Digital Ambient Light Sensor', 'Lux', 31.79]
        #   description                     unit  value
        self.labels_text = first_screen.labels_text

        self.create_graph()

        # # Construction de la courbe
        # Initialisation de la courbe avec sa couleur
        self.plot = MeshLinePlot(color=[0, 0, 0, 1])
        self.plot.points = [(0, 0)]*101

        self.graph.add_plot(self.plot)

        self.ids.graph_id.add_widget(self.graph)

        # Actualisation de la courbe
        Clock.schedule_interval(self.update, 2)

    def create_graph(self):
        """Création du graph"""

        print("Appel de la création du graph ..")

        # Paramètres du graph
        self.xlabel = 'Date'
        self.ylabel = "1 correspond à  " + str(self.y_major) + " " + self.unit
        self.xmin = 0
        self.xmax = 100
        self.ymin = 0
        self.ymax = 1
        print("self.y_major", self.y_major)

        # Je crée ou recrée
        self.graph = Graph( background_color=(0.8, 0.8, 0.8, 1),
                            border_color=(0, 0.1, 0.1, 1),
                            xlabel=self.xlabel,
                            ylabel=self.ylabel,
                            x_ticks_minor=5,
                            x_ticks_major=25,
                            y_ticks_major=0.25,
                            x_grid_label=True,
                            y_grid_label=True,
                            padding=5,
                            x_grid=True,
                            y_grid=True,
                            xmin=self.xmin,
                            xmax=self.xmax,
                            ymin=self.ymin,
                            ymax=self.ymax,
                            tick_color=(1, 0, 0, 1),
                            label_options={'color': (0.5, 0.5, 0, 1)})

    def update(self, dt):

        self.plot.points = []
        self.get_y_major()

        # Apply value to plot
        for i in range(len(self.histo)):
            y = self.histo[i][1]/self.y_major
            self.plot.points.append([i, y])

    def get_y_major(self):
        """Le maxi de l'echelle des y"""

        # Recherche du maxi
        maxi = 0
        for couple in self.histo:
            if couple[1] > maxi:
                maxi = couple[1]

        # Définition de l'échelle sur y soit 0 à self.y_major
        if 1 < maxi < 10:
            self.y_major = round(int(maxi), -0)
        elif 10 <= maxi < 100:
            self.y_major = round(int(maxi), -1)
        elif 100 <= maxi < 1000:
            self.y_major = round(int(maxi), -2)
        elif 1000 <= maxi < 10000:
            self.y_major = round(int(maxi), -3)
        elif 10000 <= maxi < 100000:
            self.y_major = round(int(maxi), -4)
        else:
            self.y_major = 1


class OwnerInfo(Popup):
    pass


class Screen1(Screen):

    btns_text = ListProperty(["Smart Citizen"]*16)
    labels_text = ListProperty(["Capteur"]*16)
    owner_titre = StringProperty("")
    owner_detail = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Liste des id chez SmartCitizen
        self.sensor_id_list = [0]*16

    def display_info(self):
        print("owner_detail\n", self.owner_detail)
        popup = OwnerInfo()
        popup.open()

    def apply_go_to_screen2(self, index):
        """Appelé par le kv à l'action sur le button index
        index est le l'indice du capteur dans la liste"""

        # Le id dont il nous faut l'histo
        sensor_id = self.sensor_id_list[index]
        print("sensor_id", sensor_id)

        # Bascule sur écran 2
        second = self.manager.get_screen("second")
        second.sensor_id = sensor_id
        if len(self.labels_text[index].split(" ")) > 1:
            second.unit = self.labels_text[index].split(" ")[1]
        else:
            second.unit = ""
        second.titre = self.btns_text[index]
        second.graph_init()
        self.manager.current = "second"


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
        Clock.schedule_interval(self.update, 2)

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
        second_screen = self.ids.sm.get_screen("second")
        sensor_id = second_screen.sensor_id
        if sensor_id:
            self.get_histo(sensor_id)

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

        smart_req = SmartCitizenRequests(self.url, self.device_nbr)
        resp = smart_req.get_resp_dict(smart_req.instant_url)

        # Détail du owner
        owner = smart_req.get_owner(resp)
        kit = smart_req.get_kit(resp)
        data = smart_req.get_data(resp)
        self.apply_owner(owner, kit, data)

        # Les valeurs de tous les capteurs
        sensors = smart_req.get_sensors(resp)
        self.apply_sensors(sensors)

    def apply_sensors(self, sensors):
        """Maj de la liste des capteurs avec unit et value"""

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
                # sensors[d][1] est le id chez smartcitizen
                first_screen.sensor_id_list[d] = sensors[d][3]

    def apply_owner(self, owner, kit, data):
        """Maj du str des infos du owner"""

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

        # Report à first_screen pour affichage dans un popup
        if kit:
            first_screen.owner_detail = kit + "\n\n"

        if data:
            if data[0] == None: data[0] = ""
            if data[1] == None: data[1] = ""
            if data[2] == None: data[2] = ""
            if data[3] == None: data[3] = ""

            # exposure  alt  latitude  longitude
            first_screen.owner_detail += "Exposition: " + str(data[0]) + "\n" +\
                                         "Altitude: " + str(data[1]) + "\n" +\
                                         "Latitude: " + str(data[2]) + "\n" +\
                                         "Longitude: " + str(data[3])

    def get_histo(self, sensor_id):
        """Le sensor id est donné par le clic sur le button du capteur.
        rollup, from_, to_ sont définis dans les options de smartcitizen.
        """

        rollup = self.app.config.get('histo', 'rollup')
        from_ = self.app.config.get('histo', 'from_')
        to_ = self.app.config.get('histo', 'to_')

        smart_req = SmartCitizenRequests(self.url, self.device_nbr)
        histo_url = smart_req.get_histo_url(sensor_id, rollup, from_, to_)

        resp = smart_req.get_resp_dict(histo_url)

        histo = smart_req.get_histo(resp)
        self.set_histo(histo, rollup, from_, to_)

    def set_histo(self, histo, rollup, from_, to_):
        if histo:
            if len(histo[0]) > 1:
                second_screen = self.ids.sm.get_screen("second")
                second_screen.histo = histo
                second_screen.histo_data = (rollup, from_, to_)
                print("Données de SmartCitizen pour le graph ok")


class SmartCitizenApp(App):

    def build(self):

        # SmartCitizen viendra chercher ces attributs
        self.device_nbr = self.config.get('url', 'kit')
        self.rollup = self.config.get('histo', 'rollup')
        self.from_ = self.config.get('histo', 'from_')
        self.to_ = self.config.get('histo', 'to_')

        return SmartCitizen(self)

    def build_config(self, config):
        config.setdefaults("font", {"font_size": 20})

        config.setdefaults("histo", {"rollup": 4,
                                     "from_": "2020-01-01",
                                     "to_": "2020-01-15"})

        config.setdefaults("url",
                          {"url": "http://api.smartcitizen.me/v0/devices/",
                           "kit": 9525})

    def build_settings(self, settings):
        data = '''[ { "type": "title",
                      "title":"Textes"},

                    { "type": "numeric",
                      "title": "Taille des textes",
                      "desc": "De 10 à 40",
                      "section": "font",
                      "key": "font_size"},

                    { "type": "title",
                      "title":"Adresse Web"},

                    { "type": "string",
                      "title": "Url sans le numéro du kit",
                      "desc": "http: ...",
                      "section": "url",
                      "key": "url"},

                    { "type": "numeric",
                      "title": "Numéro du kit",
                      "desc": "0 à 20 000",
                      "section": "url",
                      "key": "kit"},

                    { "type": "title",
                      "title":"Historique"},

                    { "type": "numeric",
                      "title": "Nombre d'heures",
                      "desc": "entre 2 valeurs: 1 à 24 heures",
                      "section": "histo",
                      "key": "rollup"},

                    { "type": "string",
                      "title": "Depuis",
                      "desc": "Date de début",
                      "section": "histo",
                      "key": "from_"},

                    { "type": "string",
                      "title": "Jusqu'à",
                      "desc": "Date de fin",
                      "section": "histo",
                      "key": "to_"}
                      ]'''

        settings.add_json_panel('Configuration de SmartCitizen',
                                 self.config,
                                 data=data)

    def on_config_change(self, config, section, key, value):
        """Si changement dans Options"""

        if config is self.config:  # du joli python rigoureux
            token = (section, key)

            # Kit number
            if token == ('kit', 'kit'):
                value = int(value)
                if value < 0: value = 0
                if value > 20000: value = 20000
                print("Nouveau kit:", value)
                # Save in ini
                self.config.set('kit', 'kit', value)
                # SmartCitizen viendra chercher cet attribut de cette class
                self.device_nbr = value

            # Rollup
            if token == ('histo', 'rollup'):
                # Nombre d'heures entre chaque relevé, 1 à 24 heures
                value = int(value)
                if value < 1: value = 1
                if value > 24: value = 24
                # Save in ini
                self.config.set('', '', value)

            # from_ et to = 2020-01-10
            if token == ('histo', 'from_'):
                # Vérification de la cohérence de la date
                try:
                    d = value.split("-")
                except:
                    d = ["2020", "01", "01"]
                try:
                    # dt = objet datetime
                    dt = datetime.date(int(d[0]), int(d[1]), int(d[2]))
                except:
                    d = ["2020", "01", "01"]
                    dt = datetime.date(int(d[0]), int(d[1]), int(d[2]))
                print("from_ datetime", dt)
                # TODO imposer from < date actuelle
                new_value = d[0] + "-" + d[1] + "-" + d[2]
                # Save in ini
                self.config.set('histo', 'from_', new_value)

            if token == ('histo', 'to_'):
                # Vérification de la cohérence de la date
                try:
                    d = value.split("-")
                except:
                    d = ["2020", "01", "01"]
                try:
                    # dt = objet datetime
                    dt = datetime.date(int(d[0]), int(d[1]), int(d[2]))
                except:
                    d = ["2020", "01", "01"]
                    dt = datetime.date(int(d[0]), int(d[1]), int(d[2]))
                print("to_ datetime", dt)
                # TODO imposer to > from
                # TODO imposer from < date actuelle
                new_value = d[0] + "-" + d[1] + "-" + d[2]
                # Save in ini
                self.config.set('histo', 'to_', new_value)

    def do_quit(self):
        SmartCitizenApp.get_running_app().stop()


def dir_detail(objet):
    for index in dir(objet):
        print(index)


if __name__ == '__main__':
    SmartCitizenApp().run()
