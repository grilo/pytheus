#!/usr/bin/env python

"""
    Barebones HTTP server.

    Do NOT use this for anything else other than Prometheus exporting.
"""

import logging
import email


class BadRequestError(Exception):
    """Unable to properly parse the request."""
    pass


class Base(object):

    """
        Attributes:
            method: GET, POST
            path: /, /metrics
            protocol: HTTP/1.0
            headers: {
                host: localhost:5000
                connection: keep-alive
            }
    """

    def __init__(self, socket, address, raw_string):

        self.socket = socket
        self.address = address
        raw_string = raw_string.strip()
        if not raw_string:
            logging.error("Empty request from: %s", address)
            raise BadRequestError

        try:
            lines = raw_string.strip().splitlines()
            logging.info("REQUEST: %s", lines[0])

            first_line = lines[0].split(' ')
            self.method = first_line[0]
            self.path = first_line[1]
            if len(first_line) == 3:
                self.protocol = first_line[2]

            self.headers = email.message_from_string('\r\n'.join(lines[1:]))
        except Exception:
            logging.error("Unable to parse request: [%s]", raw_string, exc_info=True)
            raise BadRequestError
