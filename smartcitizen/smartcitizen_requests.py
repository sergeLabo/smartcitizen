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


from time import sleep
import requests
import json


class SmartCitizenRequests:

    def __init__(self, url, device, device_nbr):
        """
        url = https://api.smartcitizen.me/v0/
        device = devices ou kits
        device_nbr = 9525
        """

        self.url = url
        self.device = device
        self.device_nbr = device_nbr

        self.request_url = self.get_request_url()
        self.data = None
        self.resp_dict = self.get_one_request()
        self.data = self.get_data()
        self.owner = self.get_owner()

    def get_request_url(self):
        """url ne doit pas se terminer par /
        device est devices ou kits, pas de /
        device_nbr entre 0 et 100000, int
        A combiner avec la saisie des options !
        """

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

    def get_one_request(self):
        """Bonne url nouvelle API
        url = "http://api.smartcitizen.me/v0/devices/9525"
        """

        resp = requests.get(self.request_url)
        c = resp.text
        resp_dict = json.loads(c)

        return resp_dict

    def get_data(self):
        """
        [["Temp", "°C", 25.3], ...  ]
        # #for i in ["description", "unit", "value"]:
        # #if i in sens_dict:
        # #print(i, sens_dict[i])
        """

        data = []
        if "data" in self.resp_dict:
            if "sensors" in self.resp_dict["data"]:
                for sens_dict in self.resp_dict["data"]["sensors"]:
                    data.append([sens_dict["description"],
                                 sens_dict["unit"],
                                 sens_dict["value"]])

        return data

    def get_owner(self):
        try:
            owner = (self.resp_dict["owner"]["username"],
                    self.resp_dict["owner"]["url"])
        except:
            owner = ("Kit", "inexistant")
        return owner


if __name__ == '__main__':

    url = "http://api.smartcitizen.me/v0/"
    device = "devices"
    device_nbr = str(9525)
    scr = SmartCitizenRequests(url, device, device_nbr)
    scr.get_one_request()

    print(scr.data, scr.owner)
