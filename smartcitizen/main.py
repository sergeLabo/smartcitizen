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


__version__ = '0.21'


import kivy
kivy.require('1.11.1')

# Pour mon PC mais perturbe l'affichage sur android
import sys
if sys.platform == 'linux':
    from kivy.core.window import Window
    # Pour simuler l'écran de mon tél qui fait 1280*720
    k = 0.80
    WS = (int(720*k), int(1280*k))
    Window.size = WS

import textwrap
import datetime

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


class Screen2(Screen):

    graph_id = ObjectProperty()
    titre = StringProperty("Capteur")

    def __init__(self, **kwargs):
        """self.graph ne peut pas être initié ici.
        Il doit être dans une autre méthode et appelé plus tard.
        """

        super().__init__(**kwargs)

        self.sensor_id = None
        self.unit = ""
        self.graph = None
        self.histo = []
        self.histo_data = None
        self.y_major = 1
        self.titre = "Capteur"
        self.period = None
        self.abscissa = 100
        self.reset = None

    def get_datetime(self, date):
        """de "2020-01-15", retourne datetime.date"""
        d = date.split("-")
        return datetime.date(int(d[0]), int(d[1]), int(d[2]))

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
        screen1 = self.manager.get_screen("screen1")
        # ['Digital Ambient Light Sensor', 'Lux', 31.79]
        #   description                     unit  value
        self.labels_text = screen1.labels_text

        self.create_graph()

        # # Construction de la courbe
        # Initialisation de la courbe avec sa couleur
        self.plot = MeshLinePlot(color=[0, 0, 0, 1])
        self.plot.points = [(0, 0)]*101

        self.graph.add_plot(self.plot)

        self.ids.graph_id.add_widget(self.graph)

        # ## Actualisation de la courbe
        # #Clock.schedule_interval(self.update, 2)

    def create_graph(self):
        """Création du graph seul et pas d'application au widget"""

        print("Appel de la création du graph ..")

        # Paramètres du graph
        self.xlabel = "Historique en heures"
        self.ylabel = "1 correspond à  " + str(self.y_major) + " " + self.unit
        self.xmin = 0
        self.xmax = self.abscissa
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
                            y_ticks_major=0.10,
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
                            label_options={'color': (0.2, 0.2, 0.2, 1)})

    def update(self):  # , dt):
        """Update de cette class toutes les 2 secondes"""

        if self.reset:
            self.reset = None
            self.graph_init()

        # Reset des points
        self.plot.points = []

        # Echelle des y
        y_major = self.get_y_major()
        if y_major != self.y_major:
            self.y_major = y_major
            # reset du graph
            self.graph_init()

        # Apply value to plot
        self.abscissa = len(self.histo)
        print(self.abscissa)
        for i in range(self.abscissa):
            y = self.histo[i][1]/self.y_major
            self.plot.points.append([i, y])

    def get_y_major(self):
        """Le maxi de l'echelle des y"""

        # Recherche du maxi
        maxi = 0
        for couple in self.histo:
            if couple[1] > maxi:
                maxi = couple[1]

        # Pour éviter que la courbe touche le maxi
        maxi *= 1.1

        # Définition de l'échelle sur y soit 0 à y_major
        if 1 < maxi < 10:
            y_major = round(int(maxi), -0)
        elif 10 <= maxi < 100:
            y_major = round(int(maxi), -1)
        elif 100 <= maxi < 1000:
            y_major = round(int(maxi), -2)
        elif 1000 <= maxi < 10000:
            y_major = round(int(maxi), -3)
        elif 10000 <= maxi < 100000:
            y_major = round(int(maxi), -4)
        else:
            y_major = 1

        return y_major


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
        screen2 = self.manager.get_screen("screen2")
        screen2.sensor_id = sensor_id
        if len(self.labels_text[index].split(" ")) > 1:
            screen2.unit = self.labels_text[index].split(" ")[1]
        else:
            screen2.unit = ""
        screen2.titre = self.btns_text[index]
        screen2.graph_init()
        self.manager.current = "screen2"


class MainScreen(Screen):

    owner = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Demande permanente du owner jusqu'à l'avoir
        Clock.schedule_interval(self.get_owner, 1)

    def get_owner(self, dt):
        if not self.owner:
            try:
                screen1 = self.manager.get_screen("screen1")
                toto = screen1.owner_titre.splitlines()[0]
                self.owner = 'Suivi des capteurs de\n{}'.format(toto)
            except:
                self.owner = ""

        return self.owner


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
        self.count = 0

        # premier appel au lancement
        Clock.schedule_once(self.update)

        # Appel tous les 2 secondes
        Clock.schedule_interval(self.update, 2)

    def update(self, dt):
        self.get_and_apply_instant_values()

        # Report dans l'écran 2
        screen2 = self.ids.sm.get_screen("screen2")

        sensor_id = screen2.sensor_id
        if sensor_id:
            self.get_histo(sensor_id)
        if self.app.reset:
            screen2.reset = 1
            self.app.reset = None

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

        smart_req = SmartCitizenRequests(self.app.url, self.app.device_nbr)
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

        # Pour bel affichage seulement
        self.count += 1

        screen1 = self.ids.sm.get_screen("screen1")

        # 2*16 Cases vides
        screen1.btns_text = [""]*16
        screen1.labels_text = [""]*16

        # Ecrasement par nouvelles valeurs
        if sensors:
            x = min(len(sensors), 16)
            for d in range(x):
                description = textwrap.fill(sensors[d][0], 30)
                screen1.btns_text[d] = description
                t = str(round(sensors[d][2], 2))\
                        + " "\
                        + sensors[d][1]
                screen1.labels_text[d] = t

                # sensors[d][3] = id
                screen1.sensor_id_list[d] = sensors[d][3]

                a = "\nRequête n° {:<8}:\nCapteur: {:>30}    valeur: {}"
                # #print(a.format(self.count, description, t))
                pass

    def apply_owner(self, owner, kit, data):
        """Maj du str des infos du owner"""

        screen1 = self.ids.sm.get_screen("screen1")

        # Reset
        screen1.owner_titre = ""

        if owner[0]:
            screen1.owner_titre = owner[0]
        else:
            screen1.owner_titre = "Owner inconnu"

        if owner[1]:
            screen1.owner_titre += "\n" + owner[1]

        # Reset
        screen1.owner_detail = ""

        # Report à screen1 pour affichage dans un popup
        if kit:
            screen1.owner_detail = kit + "\n\n"

        if data:
            if data[0] == None: data[0] = ""
            if data[1] == None: data[1] = ""
            if data[2] == None: data[2] = ""
            if data[3] == None: data[3] = ""

            # exposure  alt  latitude  longitude
            screen1.owner_detail += "Exposition: " + str(data[0]) + "\n" +\
                                         "Altitude: " + str(data[1]) + "\n" +\
                                         "Latitude: " + str(data[2]) + "\n" +\
                                         "Longitude: " + str(data[3])

    def get_histo(self, sensor_id):
        """Le sensor id est donné par le clic sur le button du capteur.
        rollup, from_, to_ sont définis dans les options de smartcitizen.
        """

        smart_req = SmartCitizenRequests(self.app.url, self.app.device_nbr)

        histo_url = smart_req.get_histo_url(sensor_id,
                                            self.app.rollup,
                                            self.app.from_,
                                            self.app.to_)
        resp = smart_req.get_resp_dict(histo_url)

        histo = smart_req.get_histo(resp)
        self.set_histo(histo)

    def set_histo(self, histo):
        if histo:
            if len(histo[0]) > 1:
                # Repord dans l'écran 2
                screen2 = self.ids.sm.get_screen("screen2")
                screen2.histo = histo
                screen2.update()
                screen2.histo_data = (self.app.rollup, self.app.from_,
                                            self.app.to_)


class SmartCitizenApp(App):

    def build(self):

        # SmartCitizen viendra chercher ces attributs
        self.device_nbr = self.config.get('url', 'kit')
        self.rollup = self.get_rollup()
        self.from_ , self.to_ = self.get_from_to()
        print("Historique depuis", self.from_ , "jusqu'à", self.to_)

        self.reset = None
        self.url = self.config.get('url', 'url')

        return SmartCitizen(self)

    def build_config(self, config):

        config.setdefaults("histo",
                          {"rollup": "6m",
                           "histo": "jour"})

        config.setdefaults("url",
                          {"url": "http://api.smartcitizen.me/v0/devices/",
                           "kit": 9525})

    def build_settings(self, settings):
        data = '''[ { "type": "title",
                      "title": "Adresse Web"},

                    { "type": "string",
                      "title": "Url sans le numéro du kit",
                      "desc": "http: ...",
                      "section": "url",
                      "key": "url"},

                    { "type": "numeric",
                      "title": "Numéro du kit",
                      "desc": "0 à 99 999",
                      "section": "url",
                      "key": "kit"},

                    { "type": "title",
                      "title": "Historique"},

                    { "type": "string",
                      "title": "Période",
                      "desc": "Jour ou semaine",
                      "section": "histo",
                      "key": "histo"}
                    ]
                '''

        settings.add_json_panel('Configuration de SmartCitizen',
                                 self.config,
                                 data=data)

    def on_config_change(self, config, section, key, value):
        """Si changement dans Options"""

        if config is self.config:  # du joli python rigoureux
            token = (section, key)

            # url
            if token == ('url', 'url'):
                url = check_request_url(value)
                print("Nouvelle url:", url)
                # Save in ini
                self.config.set('url', 'url', url)
                # SmartCitizen viendra chercher cet attribut de cette class
                self.url = url

            # Kit number
            if token == ('url', 'kit'):
                value = int(value)
                if value < 0: value = 0
                if value > 20000: value = 20000
                print("Nouveau kit:", value)
                # Save in ini
                self.config.set('url', 'kit', value)
                # SmartCitizen viendra chercher cet attribut de cette class
                self.device_nbr = value

            # Histo
            if token == ('histo', 'histo'):
                # Jour ou semaine
                value = int(value)
                if value == "jour":
                    value = "jour"
                if value == "semaine":
                    value = "semaine"
                # Save in ini
                self.config.set('histo', 'histo', value)
                self.reset = 1

    def check_request_url(self, url):
        """url doit se terminer par /"""

        if "api.smartcitizen.me" not in url:
            url = None
        if url:
            if not url[-1] == "/":
                url += "/"

        return request_url

    def get_rollup(self):
        """API SC: rollup = str = 6m = 6 minutes
                y years
                M months
                w weeks
                d days
                h hours
                m minutes
                s seconds
                ms milliseconds
        Si period = 1j: rollup = "6m" --> 144 valeurs
        si period = 7j: rollup = "1h" --> 168 valeurs
        """

        if self.config.get('histo', 'histo') == "jour":
            rollup = "6m"
        else:
            rollup = "1h"

        return rollup

    def get_from_to(self):
        d = datetime.date.today()
        t = d.timetuple()
        to_ = str(t[0]) + "-" + str(t[1]) + "-" + str(t[2])
        print("Date du jour", to_)

        if self.config.get('histo', 'histo') == "jour":
            from_ = str(t[0]) + "-" + str(t[1]) + "-" + str(t[2] - 1)
        else:
            from_ = str(t[0]) + "-" + str(t[1]) + "-" + str(t[2] - 7)


        return from_ , to_

    def do_quit(self):
        SmartCitizenApp.get_running_app().stop()


def dir_detail(objet):
    for index in dir(objet):
        print(index)


if __name__ == '__main__':
    SmartCitizenApp().run()
