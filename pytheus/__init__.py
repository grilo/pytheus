#!/usr/bin/env python

import pytheus.exporter

def start(address="0.0.0.0", port=8000):
    exporter = pytheus.exporter.Base(address, port)
    exporter.start()
