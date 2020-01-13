#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import json

# 'https://api.github.com/events'
url_all = 'https://api.smartcitizen.me/v0/kits'

url = 'https://api.smartcitizen.me/v0/kits/9525'

"""
smartcitizen.me:
    https://smartcitizen.me/kits/9525

API:
    https://developer.smartcitizen.me/#authentication

# Dans firefox, https://api.smartcitizen.me/v0/kits/9525 retourne
{"id":"record_not_found", "message":"Couldn't find Kit with 'id'=9525", "url":"", "errors":""}

Pour obtenir un token
# Send authenticated POST for username 'user1', which should return the 'access_token'
$ curl -XPOST https://api.smartcitizen.me/v0/sessions -d "username=user1" -d "password=password"
"""


TOKEN = "3135dd8ea0e628c3703e8e46bc8b70c8be81eebfb9f32c1065a4b3ff98dc4fc3"
HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}

for i in range(9580, 9590):
    url = 'https://api.smartcitizen.me/v0/kits/' + str(i)
    print(url)
    resp = requests.get(url, HEADERS)
    c = resp.text
    d = json.loads(c)

    if d['id'] != 'record_not_found':
        print(i, d['uuid'])
