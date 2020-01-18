#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inspiré de:
https://github.com/kivy/plyer/tree/master/examples/accelerometer/using_graph
"""

from math import sin

import kivy
kivy.require('1.11.1')
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock

class GraphExample(BoxLayout):

    graph = ObjectProperty()

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.tictac = 0

        print([type(widget) for widget in self.walk(loopback=True)])
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]

        # Appel du widget avec l'id graph
        self.ids.graph.add_plot(self.plot)

        Clock.schedule_interval(self.update, 0.1)

    def update(self, dt):
        self.tictac += 1
        self.plot.points = [(x, sin((x + self.tictac)/10.0)) for x in range(0, 101)]


class GraphExampleApp(App):
    def build(self):
        return GraphExample()

if __name__ == '__main__':
    GraphExampleApp().run()
