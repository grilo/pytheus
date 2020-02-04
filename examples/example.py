#!/usr/bin/env python

import pytheus.exporter
from pytheus.decorators import *

@gauge("blahblah")
def fake():
    import time
    time.sleep(2)
    return time.time(), {"tag": "hello world!"}

@gauge("blahblah")
def anotherfake():
    import time
    time.sleep(5)
    raise Exception
    return time.time(), {"tag": "bye world!"}

exporter = pytheus.exporter.Base("0.0.0.0", 8000)
exporter.start()

