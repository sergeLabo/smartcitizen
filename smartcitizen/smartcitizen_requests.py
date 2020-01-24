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

    def __init__(self, url, device_nbr):
        """
        url = http://api.smartcitizen.me/v0/devices/
        device_nbr = 9525 = int
        """

        self.url = url
        self.device_nbr = device_nbr

        self.instant_url = self.get_instant_url()

    def get_instant_url(self):
        """L'url pour requête des valeurs instantanées.
        Les contrôles de la cohérence de l'url doivent être fait
        avant l'appel de cette class
        avec / à la fin de self.url
        """

        instant_url = self.url + str(self.device_nbr)
        # #print("Adresse des requêtes: {}".format(instant_url))

        return instant_url

    def get_histo_url(self, id_, rollup, from_, to_):
        """
        id_ = 55
        rollup = 4
        from_ = '2020-01-01'
        to_ = '2020-01-15'

        histo_url = 'http://api.smartcitizen.me/v0/devices/9525/readings?sens
        or_id=55&rollup=4h&from=2020-01-01&to=2020-01-15'
                     http://api.smartcitizen.me/v0/devices/9525/readings?sens
        or_id=55&rollup=4h&from=2020-01-01&to=2020-01-15
        """

        histo_url = self.url + str(self.device_nbr)\
                    + '/readings?sensor_id=' + str(id_)\
                    + '&rollup=' + str(rollup) + '&from='\
                    + from_ + '&to=' + to_

        return histo_url

    def get_resp_dict(self, url):
        """Retourne le dict de la requête"""

        resp = requests.get(url)
        c = resp.text
        resp_dict = json.loads(c)
        if isinstance(resp_dict, dict):
            return resp_dict
        else:
            print("La réponse n'est pas un dictionnaire")
            return None

    def get_sensors(self, resp):
        """Les valeurs instantanées de tous les capteurs en liste:
        'sensors': [

        {'id': 113,
        'ancestry': '111',
        'name': 'AMS CCS811 - TVOC',
        'description': 'Total Volatile Organic Compounds Digital Indoor Sensor',
        'unit': 'ppb',
        'created_at': '2019-03-21T16:43:37Z',
        'updated_at': '2019-03-21T16:43:37Z',
        'measurement_id': 47,
        'uuid': '0c2a1afc-dc08-4066-aacb-0bde6a3ae6f5',
        'value': 99.0,
        'raw_value': 99.0,
        'prev_value': 99.0,
        'prev_raw_value': 99.0},
        """

        sensors = []
        try:
            for sens_dict in resp["data"]["sensors"]:
                sensors.append([sens_dict["description"],
                             sens_dict["unit"],
                             sens_dict["value"],
                             sens_dict["id"]])
        except:
            sensors = None

        return sensors

    def get_owner(self, resp):
        """Données du owner
        'owner':

            {'id': 7027,
            'uuid': 'b57c4db5-de3b-4719-9bd2-f7fc24c64bb9',
            'username': 'la labomedia',
            'avatar': 'https://smartcitizen.s3.amazonaws.com/avatars/default.svg',
            'url': 'https://labomedia.org',
            'joined_at': '2019-06-05T14:48:56Z',
            'location':
                {'city': 'Orléans',
                'country': 'France',
                'country_code': 'FR'},
            'device_ids': []}
        """

        try:
            username = (resp["owner"]["username"])
        except:
            username = None

        try:
            url = (resp["owner"]["url"])
        except:
            url = None

        try:
            city = (resp["owner"]["location"]["city"])
        except:
            city = None

        try:
            country = (resp["owner"]["location"]["country"])
        except:
            country = None


        return [username, url, city, country]

    def get_kit(self, resp):
        """Caractéristiques du kit
        'kit':
            {'id': 26,
            'uuid': '56bec177-6d93-4001-b700-1abd8347ed87',
            'slug': 'sck:2,1',
            'name': 'SCK 2.1',
            'description': 'Smart Citizen Kit 2.1 with Urban Sensor Board',
            'created_at': '2019-03-21T17:02:46Z',
            'updated_at': '2019-03-21T17:02:46Z'}}
        """

        try:
            kit_description = (resp["kit"]["description"])
        except:
            kit_description = None

        return kit_description

    def get_data(self, resp):
        """Spécificité de la position des capteurs
        'data':
            {'recorded_at': '2020-01-16T17:29:51Z',
            'added_at': '2020-01-16T17:29:51Z',
            'location':
                {   'ip': None,
                    'exposure': 'outdoor',
                    'elevation': None,
                    'latitude': 47.9006640998651,
                    'longitude': 1.91683530807495,
                    'geohash': 'u092e85c96',
                    'city': 'Orléans',
                    'country_code': 'FR',
                    'country': 'France'},
        """

        try:
            exposure = (resp["data"]["location"]["exposure"])
        except:
            exposure = None

        try:
            elevation = (resp["data"]["location"]["elevation"])
        except:
            elevation = None

        try:
            latitude = (resp["data"]["location"]["latitude"])
        except:
            latitude = None

        try:
            longitude = (resp["data"]["location"]["longitude"])
        except:
            longitude = None

        return [exposure, elevation, latitude, longitude]

    def get_histo(self, resp):
        """L'historique d'un capteur défini par son id
        [
        ['2020-01-14T20:00:35Z', 18.709495798319324],
        ['2020-01-14T16:00:32Z', 18.996260504201675],
        ...]
        """

        try:
            histo = resp['readings']
        except:
            histo = None

        return histo


if __name__ == '__main__':

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    url = "http://api.smartcitizen.me/v0/devices/"
    device_nbr = 9525
    scr = SmartCitizenRequests(url, device_nbr)

    resp = scr.get_resp_dict(scr.instant_url)

    # instant
    owner = scr.get_owner(resp)
    print("owner")
    pp.pprint(owner)
    sensors = scr.get_sensors(resp)
    print("sensors")
    pp.pprint(sensors)
    kit = scr.get_kit(resp)
    print("kit")
    pp.pprint(kit)
    data = scr.get_data(resp)
    print("data")
    pp.pprint(data)

    # histo
    id_ = 113
    rollup = "4h"
    from_ = "2020-01-01"
    to_ = "2020-01-15"
    histo_url = scr.get_histo_url(id_, rollup, from_, to_)
    # http://api.smartcitizen.me/v0/devices/9525/readings?sensor_id=113&rollup=6m&from=2020-1-23&to=2020-1-24
    print(histo_url)
    resp = scr.get_resp_dict(histo_url)
    h = scr.get_histo(resp)
    print("h", h)
    print(len(h))
    # #pp.pprint(h)

# Réponse du script
"""
Adresse des requêtes: http://api.smartcitizen.me/v0/devices/9525
owner
('la labomedia', 'https://labomedia.org', 'Orléans', 'France')
sensors
[   [   'Total Volatile Organic Compounds Digital Indoor Sensor',
        'ppb',
        108.0,
        113],
    ['Equivalent Carbon Dioxide Digital Indoor Sensor', 'ppm', 1110.0, 112],
    ['Digital Ambient Light Sensor', 'Lux', 31.79, 14],
    ['Custom Circuit', '%', -1.0, 10],
    [   'I2S Digital Mems Microphone with custom Audio Processing Algorithm',
        'dBA',
        47.82,
        53],
    ['Digital Barometric Pressure Sensor', 'K Pa', 100.6, 58],
    ['Particle Matter PM 1', 'ug/m3', 4.0, 89],
    ['Particle Matter PM 10', 'ug/m3', 7.0, 88],
    ['Particle Matter PM 2.5', 'ug/m3', 6.0, 87],
    ['Humidity', '%', 54.42, 56],
    ['Temperature', 'ºC', 18.9, 55]]
kit
'Smart Citizen Kit 2.1 with Urban Sensor Board'
data
('outdoor', None, 47.9006640998651, 1.91683530807495)
h
[   ['2020-01-14T20:00:35Z', 18.709495798319324],
    ['2020-01-14T16:00:32Z', 18.996260504201675],
.....
"""

# instant value
"""
{'id': 9525,
'uuid': '6f197dc0-a7bf-495d-bf36-da5ee129a1f6',
'name': 'la Labomedia',
'description': 'Smart Citizen Kit 2.1 with Urban Sensor Board',
'state': 'has_published',
'hardware_info':

    {'id': '2D74A78050515157382E3120FF14213E', 'mac': '3E:71:BF:30:2C:32', 'time': '2020-01-16T03:00:17Z', 'esp_bd': '', 'hw_ver': '2.1', 'sam_bd': '2019-05-07T02:45:29Z', 'esp_ver': '', 'sam_ver': '0.9.1-30e1776'},

'system_tags': ['online', 'outdoor'],
'user_tags': ['Experimental', 'First Floor'],
'is_private': False,
'notify_low_battery': False,
'notify_stopped_publishing': False,
'last_reading_at': '2020-01-16T17:29:51Z',
'added_at': '2019-06-05T14:48:57Z',
'updated_at': '2020-01-16T03:00:22Z',
'mac_address': '[FILTERED]',
'owner':

    {   'id': 7027,
        'uuid': 'b57c4db5-de3b-4719-9bd2-f7fc24c64bb9',
        'username': 'la labomedia',
        'avatar': 'https://smartcitizen.s3.amazonaws.com/avatars/default.svg',
        'url': 'https://labomedia.org',
        'joined_at': '2019-06-05T14:48:56Z',
        'location':
            {'city': 'Orléans',
            'country': 'France',
            'country_code': 'FR'},
        'device_ids': []},

'data':

    {   'recorded_at': '2020-01-16T17:29:51Z',
        'added_at': '2020-01-16T17:29:51Z',
        'location':
            {   'ip': None,
                'exposure': 'outdoor',
                'elevation': None,
                'latitude': 47.9006640998651,
                'longitude': 1.91683530807495,
                'geohash': 'u092e85c96',
                'city': 'Orléans',
                'country_code': 'FR',
                'country': 'France'},

        'sensors': [

            {'id': 113, 'ancestry': '111', 'name': 'AMS CCS811 - TVOC', 'description': 'Total Volatile Organic Compounds Digital Indoor Sensor', 'unit': 'ppb', 'created_at': '2019-03-21T16:43:37Z', 'updated_at': '2019-03-21T16:43:37Z', 'measurement_id': 47, 'uuid': '0c2a1afc-dc08-4066-aacb-0bde6a3ae6f5', 'value': 99.0, 'raw_value': 99.0, 'prev_value': 99.0, 'prev_raw_value': 99.0},

            {'id': 112, 'ancestry': '111', 'name': 'AMS CCS811 - eCO2', 'description': 'Equivalent Carbon Dioxide Digital Indoor Sensor', 'unit': 'ppm', 'created_at': '2019-03-21T16:43:37Z', 'updated_at': '2019-03-21T16:43:37Z', 'measurement_id': 46, 'uuid': '995343c9-12ac-40c0-b6b9-19699e524f86', 'value': 1053.0, 'raw_value': 1053.0, 'prev_value': 1053.0, 'prev_raw_value': 1053.0},

            {'id': 14, 'ancestry': None, 'name': 'BH1730FVC', 'description': 'Digital Ambient Light Sensor', 'unit': 'Lux', 'created_at': '2015-02-02T18:24:56Z', 'updated_at': '2015-07-05T19:57:36Z', 'measurement_id': 3, 'uuid': 'ac4234cf-d2b7-4cfa-8765-9f4477e2de5f', 'value': 38.48, 'raw_value': 38.48, 'prev_value': 37.97, 'prev_raw_value': 37.97},

            {'id': 10, 'ancestry': None, 'name': 'Battery SCK 1.1', 'description': 'Custom Circuit', 'unit': '%', 'created_at': '2015-02-02T18:18:00Z', 'updated_at': '2015-07-05T19:53:51Z', 'measurement_id': 7, 'uuid': 'c9ff2784-53a7-4a84-b0fc-90ecc7e313f9', 'value': -1.0, 'raw_value': -1.0, 'prev_value': -1.0, 'prev_raw_value': -1.0},

            {'id': 53, 'ancestry': '52', 'name': 'ICS43432 - Noise', 'description': 'I2S Digital Mems Microphone with custom Audio Processing Algorithm', 'unit': 'dBA', 'created_at': '2018-05-03T10:42:47Z', 'updated_at': '2018-05-03T10:42:54Z', 'measurement_id': 4, 'uuid': 'f508548e-3fd1-44aa-839b-9bd147168481', 'value': 58.49, 'raw_value': 58.49, 'prev_value': 58.82, 'prev_raw_value': 58.82},

            {'id': 58, 'ancestry': '57', 'name': 'MPL3115A2 - Barometric Pressure', 'description': 'Digital Barometric Pressure Sensor', 'unit': 'K Pa', 'created_at': '2018-05-03T10:49:17Z', 'updated_at': '2018-05-03T10:49:17Z', 'measurement_id': 25, 'uuid': 'cadd2459-6559-4d92-aed1-ba04c557fed8', 'value': 100.54, 'raw_value': 100.54, 'prev_value': 100.54, 'prev_raw_value': 100.54},

            {'id': 89, 'ancestry': '86', 'name': 'PMS5003_AVG-PM1', 'description': 'Particle Matter PM 1', 'unit': 'ug/m3', 'created_at': '2018-05-22T13:20:34Z', 'updated_at': '2018-05-22T13:20:34Z', 'measurement_id': 27, 'uuid': 'a4b9efba-241f-446e-9cf2-918f25efd0c5', 'value': 5.0, 'raw_value': 5.0, 'prev_value': 9.0, 'prev_raw_value': 9.0},

            {'id': 88, 'ancestry': '86', 'name': 'PMS5003_AVG-PM10', 'description': 'Particle Matter PM 10', 'unit': 'ug/m3', 'created_at': '2018-05-22T13:20:34Z', 'updated_at': '2018-05-22T13:20:34Z', 'measurement_id': 13, 'uuid': 'c2072a22-4d81-4d7c-a38c-af9458b8f309', 'value': 6.0, 'raw_value': 6.0, 'prev_value': 13.0, 'prev_raw_value': 13.0},

            {'id': 87, 'ancestry': '86', 'name': 'PMS5003_AVG-PM2.5', 'description': 'Particle Matter PM 2.5', 'unit': 'ug/m3', 'created_at': '2018-05-22T13:20:34Z', 'updated_at': '2018-05-22T13:20:34Z', 'measurement_id': 14, 'uuid': '9ee89ac2-0482-46dd-905f-0b7a1bb12c55', 'value': 6.0, 'raw_value': 6.0, 'prev_value': 13.0, 'prev_raw_value': 13.0},

            {'id': 56, 'ancestry': '54', 'name': 'SHT31 - Humidity', 'description': 'Humidity', 'unit': '%', 'created_at': '2018-05-03T10:47:17Z', 'updated_at': '2018-05-03T10:47:17Z', 'measurement_id': 2, 'uuid': 'b6543356-0066-4bea-8ad2-687e282f9c20', 'value': 53.51, 'raw_value': 53.51, 'prev_value': 53.46, 'prev_raw_value': 53.46},

            {'id': 55, 'ancestry': '54', 'name': 'SHT31 - Temperature', 'description': 'Temperature', 'unit': 'ºC', 'created_at': '2018-05-03T10:47:15Z', 'updated_at': '2018-05-03T10:47:15Z', 'measurement_id': 1, 'uuid': '384e46a2-80dd-481e-a9fc-cfbd512f9f43', 'value': 20.18, 'raw_value': 20.18, 'prev_value': 20.22, 'prev_raw_value': 20.22}
            ]},

'kit':

    {   'id': 26,
        'uuid': '56bec177-6d93-4001-b700-1abd8347ed87',
        'slug': 'sck:2,1',
        'name': 'SCK 2.1',
        'description': 'Smart Citizen Kit 2.1 with Urban Sensor Board',
        'created_at': '2019-03-21T17:02:46Z',
        'updated_at': '2019-03-21T17:02:46Z'}}

"""

# histo
# 2015-07-28&to=2015-07-30

"""
{'device_id': 9525,
'sensor_key': 't',
'sensor_id': 55,
'component_id': 240,
'rollup': '4h',
'function': 'avg',
'from': '2020-01-01T00:00:00Z',
'to': '2020-01-15T00:00:00Z',
'sample_size': 13247,

'readings': [

['2020-01-14T20:00:35Z', 18.709495798319324],
['2020-01-14T16:00:32Z', 18.996260504201675],
['2020-01-14T12:00:59Z', 18.28696202531644],
['2020-01-14T08:00:46Z', 17.89411016949151],
['2020-01-14T04:00:40Z', 17.340672268907564],
['2020-01-14T00:00:26Z', 17.348559322033886],
['2020-01-13T20:00:13Z', 18.04076271186442],
['2020-01-13T16:00:09Z', 18.417531380753122],
['2020-01-13T12:00:04Z', 17.59974789915966],
['2020-01-13T08:00:51Z', 17.08208888888888],
['2020-01-13T04:00:07Z', 16.45914893617022],
['2020-01-13T00:00:45Z', 15.942500000000011],
['2020-01-12T20:01:00Z', 16.104827586206913],
['2020-01-12T16:01:49Z', 16.226914893617014],
['2020-01-12T12:11:10Z', 16.28756756756757],
['2020-01-12T08:01:38Z', 16.34326923076923],
['2020-01-12T04:00:05Z', 16.576516853932574],
['2020-01-12T01:33:17Z', 16.999166666666664],
['2020-01-11T22:34:55Z', 18.380000000000003],
['2020-01-11T16:00:18Z', 19.040000000000003],
['2020-01-11T12:00:58Z', 18.9462365591398],
['2020-01-11T08:02:05Z', 18.031941176470593],
['2020-01-11T04:00:27Z', 17.605939393939398],
['2020-01-11T00:01:13Z', 17.76141592920356],
['2020-01-10T20:28:34Z', 18.459272727272722],
['2020-01-10T16:00:27Z', 19.26481927710844],
['2020-01-10T12:00:22Z', 18.933030303030304],
['2020-01-10T08:00:16Z', 18.604454545454544],
['2020-01-10T04:00:35Z', 18.244556962025307],
['2020-01-10T00:02:13Z', 18.421313559322023],
['2020-01-09T20:00:24Z', 19.131640211640214],
['2020-01-09T16:00:33Z', 19.93603092783504],
['2020-01-09T12:00:09Z', 19.358342857142855],
['2020-01-09T10:23:57Z', 19.236979166666682],
['2020-01-06T08:00:11Z', 16.328],
['2020-01-06T04:00:29Z', 15.856540084388165],
['2020-01-06T00:00:08Z', 15.715991561181449],
['2020-01-05T20:00:11Z', 16.228571428571417],
['2020-01-05T16:00:43Z', 16.90966244725736],
['2020-01-05T12:00:23Z', 16.469957983193275],
['2020-01-05T08:00:52Z', 16.194621848739498],
['2020-01-05T04:00:21Z', 16.284285714285694],
['2020-01-05T00:00:12Z', 16.543991596638616],
['2020-01-04T20:00:10Z', 17.125648535564874],
['2020-01-04T16:00:17Z', 17.875439330543934],
['2020-01-04T12:00:29Z', 17.13882352941177],
['2020-01-04T08:00:20Z', 15.758158995815899],
['2020-01-04T04:00:32Z', 15.881715481171574],
['2020-01-04T00:00:36Z', 16.288493723849353],
['2020-01-03T20:00:16Z', 16.710418410041836],
['2020-01-03T16:00:45Z', 16.474537815126038],
['2020-01-03T12:00:26Z', 15.89280334728033],
['2020-01-03T08:00:55Z', 15.641308016877646],
['2020-01-03T04:00:27Z', 15.704327731092416],
['2020-01-03T00:00:02Z', 15.746764705882336],
['2020-01-02T20:00:50Z', 15.79630252100841],
['2020-01-02T16:00:23Z', 15.826166666666687],
['2020-01-02T12:00:16Z', 15.68815899581592],
['2020-01-02T08:00:14Z', 15.515829787234063],
['2020-01-02T04:00:22Z', 15.47331932773108],
['2020-01-02T00:00:48Z', 15.428067226890734],
['2020-01-01T20:00:24Z', 15.426541666666646],
['2020-01-01T16:00:52Z', 15.358739495798318],
['2020-01-01T12:00:58Z', 15.261476793248978],
['2020-01-01T08:00:54Z', 15.132405063291133],
['2020-01-01T04:00:32Z', 15.151176470588238],
['2020-01-01T00:00:23Z', 15.1797489539749]

]
}

"""
