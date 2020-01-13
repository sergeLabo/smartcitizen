#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import print_function
import treq
from twisted.internet import defer, task
from twisted.python.log import err

@defer.inlineCallbacks
def display(response):
    content = yield treq.content(response)
    print('Content: {0}'.format(content))

def main(reactor):
    d = treq.get('https://api.smartcitizen.me/v0/kits/9525')
    d.addCallback(display)
    d.addErrback(err)
    return d

task.react(main)


"""
Get All Kits
http GET https://api.smartcitizen.me/v0/kits

Get a single Kit
http GET https://api.smartcitizen.me/v0/kits/9525
"""
