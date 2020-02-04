#!/usr/bin/env python

import logging

import pytheus.collector
import pytheus.http.server
import pytheus.http.response


class Base(object):

    def __init__(self, address="0.0.0.0", port=8000, certfile=None):
        self.server = pytheus.http.server.Base(address,
                                               port,
                                               certfile,
                                               self.handle_request)
        self.collector = pytheus.collector.Base()

    def handle_request(self, request):
        response = pytheus.http.response.Base(200)
        response.content_type = "text/plain"
        response.content = self.collector.get_metrics()
        return response

    def start(self):
        self.server.serve_forever()
