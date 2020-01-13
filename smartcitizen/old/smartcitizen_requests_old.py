#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json


class SmartCityzenRequests:

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

        if "data" in resp_dict:
            if "sensors" in resp_dict["data"]:
                for sens_dict in resp_dict["data"]["sensors"]:
                    for i in ["description", "unit", "value"]:
                        if i in sens_dict:
                            print(i, sens_dict[i])
        return resp_dict


if __name__ == '__main__':

    url = "http://api.smartcitizen.me/v0/"
    device = "devices"
    device_nbr = str(9565)
    scr = SmartCityzenRequests(url, device, device_nbr)
    scr.get_one_request()



"""
id  14
ancestry    null
name    "BH1730FVC"
description "Digital Ambient Light Sensor"
unit    "Lux"
created_at  "2015-02-02T18:24:56Z"
updated_at  "2015-07-05T19:57:36Z"
measurement_id  3
uuid    "ac4234cf-d2b7-4cfa-8765-9f4477e2de5f"
value   12.61
raw_value   12.61
prev_value  12.61
prev_raw_value  12.61

{'notice': 'Welcome. The old API has been removed.',
'api_documentation_url': 'https://developer.smartcitizen.me',
'current_user_url': 'http://api.smartcitizen.me/v0/me',
'components_url': 'http://api.smartcitizen.me/v0/components',
'devices_url': 'http://api.smartcitizen.me/v0/devices',
'kits_url': 'http://api.smartcitizen.me/v0/kits',
'measurements_url': 'http://api.smartcitizen.me/v0/measurements',
'sensors_url': 'http://api.smartcitizen.me/v0/sensors',
'users_url': 'http://api.smartcitizen.me/v0/users',
'tags_url': 'http://api.smartcitizen.me/v0/tags',
'tags_sensors_url': 'http://api.smartcitizen.me/v0/tag_sensors',
'version_git': '1.1.5\n'}

smartcitizen.me:
    https://smartcitizen.me/kits/9525

API:
    https://developer.smartcitizen.me/#authentication

# Dans firefox, https://api.smartcitizen.me/v0/kits/9525 retourne
{"id":"record_not_found", "message":"Couldn't find Kit with 'id'=9525", "url":"", "errors":""}

Pour obtenir un token

S'inscrire sur smartcitizen.me
# Send authenticated POST for username 'user1', which should return the 'access_token'
$ curl -XPOST https://api.smartcitizen.me/v0/sessions -d "username=user1" -d "password=password"

url_all = 'https://api.smartcitizen.me/v0/kits'
url = 'https://api.smartcitizen.me/v0/kits/9525'

TOKEN = ""
HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}


for i in range(9525, 9526):
    # https://api.smartcitizen.me/v0/devices/9525
    url = 'https://api.smartcitizen.me/v0/devices/' + str(i)
    print(i, url)
    resp = requests.get(url, HEADERS)
    c = resp.text
    d = json.loads(c)

    if d['id'] != 'record_not_found':
        print(i, d['uuid'])

    for it in d["data"]["sensors"]:
        for key, val in it.items():
            print(key, val)


id 113
ancestry 111
name AMS CCS811 - TVOC
description Total Volatile Organic Compounds Digital Indoor Sensor
unit ppb
created_at 2019-03-21T16:43:37Z
updated_at 2019-03-21T16:43:37Z
measurement_id 47
uuid 0c2a1afc-dc08-4066-aacb-0bde6a3ae6f5
value 177.0
raw_value 177.0
prev_value 158.0
prev_raw_value 158.0
"""
