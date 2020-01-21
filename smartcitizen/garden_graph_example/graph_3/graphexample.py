#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from math import sin

import kivy
kivy.require('1.11.1')
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock

class MyGraph(Graph):
    pass

class GraphExample(BoxLayout):

    graph_id = ObjectProperty()

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # Pour initier le graph
        Clock.schedule_once(self.graph_init)

        self.tictac = 0
        Clock.schedule_interval(self.update, 0.1)

    def graph_init(self, dt):
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]

        # Appel du widget avec l'id graph
        self.ids.graph_id.add_plot(self.plot)

    def update(self, dt):
        self.tictac += 1
        self.plot.points = [(x, sin((x + self.tictac)/10.0)) for x in range(0, 101)]

class GraphExampleApp(App):
    def build(self):
        return GraphExample()

if __name__ == '__main__':
    GraphExampleApp().run()
