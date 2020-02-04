#!/usr/bin/env python

"""
    Barebones HTTP server.

    Do NOT use this for anything else other than Prometheus exporting.
"""

import logging
import os
import socket
import ssl

import pytheus.http.request
import pytheus.http.response


class CertNotFoundError(Exception):
    """When the certificate file isn't found or not readable."""
    pass

class InvalidHandlerImplementation(Exception):
    """When the response handler returns an incorrect response object."""
    pass


class Base(object):

    def __init__(self,
                 address="0.0.0.0",
                 port=7777,
                 certfile=None,
                 response_handler=None):

        self.address = address
        self.port = port
        self.certfile = certfile
        self.request_handler = pytheus.http.request.Base
        self.response_handler = response_handler

        if not self.certfile:
            logging.warning("No certificate specified, using bare http.")
        elif not os.path.isfile(self.certfile):
            raise CertNotFoundError("Unable to find certificate in: %s" % (self.certfile))

        if not self.response_handler:
            logging.error("No response handler defined, httpd will be useless!")
            self.response_handler = self._debug_response_handler

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Disable nagle algorithm, makes us look better in benchmarks
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.bind((self.address, self.port))
        self.sock.listen(10)

    def serve_forever(self):
        logging.info("Starting http server: %s:%i", self.address, self.port)
        while True:
            try:
                self.sock.settimeout(2)
                sock, addr = self.sock.accept()

                if self.certfile:
                    sock = ssl.wrap_socket(sock, certfile=self.certfile, server_side=True)

                logging.debug("Received connection: %s %s", sock, addr)
                self.handle_connection(sock, addr)

            except socket.error: # Timeout
                logging.debug("No connections received, recycling.")

    def handle_connection(self, sock, address):

        data = sock.recv(8192) # Should be enough for everybody
        response = pytheus.http.response.Base(500)

        try:
            request = pytheus.http.request.Base(sock, address, data)
            response = self.response_handler(request)
            if not isinstance(response, pytheus.http.response.Base):
                raise InvalidHandlerImplementation("Must return a pytheus.http.response.Base object.")
        except pytheus.http.request.BadRequestError:
            response = pytheus.http.response.Base(400)
        finally:
            sock.sendall(response.to_string())
            sock.close()

    @staticmethod
    def _debug_response_handler(request):
        logging.info("Got request: %s/%s", request.method, request.path)
        response = pytheus.http.response.Base(200)
        response.content_type = "text/html"
        response.content = "<html><h1>Well done!</h1></html>"
        return response
