#!/usr/bin/env python

import logging
import collections
import traceback
import Queue
import threading


# Inspired by: https://stackoverflow.com/questions/2829329
class ExceptionThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

    def run(self):
        try:
            self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
        except Exception:
            logging.critical(traceback.format_exc())


class Base(object):

    decorators = collections.OrderedDict()

    @staticmethod
    def register(metric, function):
        logging.info("Registering %s: %s", metric.__class__.__name__, function.__name__)
        Base.decorators[metric] = {
            "exec": function,
            "thread": None,
            "current_response": None,
            "last_response": "",
        }

    def get_metrics(self):

        string = ""

        for metric, properties in Base.decorators.items():
            if not properties["thread"]:
                logging.debug("Spawning new thread for %s: %s",
                              metric.__class__.__name__,
                              properties["exec"].__name__)
                queue = Queue.Queue()
                thread = ExceptionThread(target=lambda q: q.put(properties["exec"]()),
                                         args=(queue,))
                thread.start()
                Base.decorators[metric]["thread"] = thread
                Base.decorators[metric]["current_response"] = queue
            elif properties["thread"].isAlive():
                pass
            else:
                try:
                    result = properties["current_response"].get_nowait()
                    metric.measure(result[0], **result[1])
                    Base.decorators[metric]["last_response"] = metric.to_string()
                except Queue.Empty:
                    logging.warning("Retrying failed collector...")
                Base.decorators[metric]["thread"] = None

            if Base.decorators[metric]["last_response"]:
                string += Base.decorators[metric]["last_response"]

        return string
