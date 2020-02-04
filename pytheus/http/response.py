#!/usr/bin/env python

"""
    Barebones HTTP server.

    Do NOT use this for anything else other than Prometheus exporting.
"""

import logging
import datetime


class Base(object):

    codes = {
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
    }

    def __init__(self, code=200):
        self.content = ''
        self.code = code
        self.protocol = 'HTTP/1.0'
        self.server = "Promenade/0.1 (noarch)"
        self.last_modified = ''
        self.content_type = 'text/html'
        self._redirect = None
        self._last_modified = None

    @property
    def date(self):
        """Return a string representation of a date according to RFC 1123
        (HTTP/1.0).
        The supplied date must be in UTC.
        """
        now = datetime.datetime.now()
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][now.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][now.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, now.day, month,
                                                        now.year, now.hour,
                                                        now.minute, now.second)

    @property
    def content_length(self):
        return str(len(self.content))

    @property
    def last_modified(self):
        if not self._last_modified:
            self._last_modified = self.date
        return self._last_modified

    @property
    def redirect(self):
        return self._redirect

    @redirect.setter
    def redirect(self, new_url):
        self.code = 301
        self._redirect = new_url

    @last_modified.setter
    def last_modified(self, value):
        self._last_modified = value

    def to_string(self):
        header = ' '.join([self.protocol, str(self.code), Base.codes[self.code]])
        logging.debug("RESPONSE: %s", header)
        out = [
            header,
            'Date: ' + self.date,
            'Server: ' + self.server,
            'Last-Modified: ' + self.last_modified,
            'Content-Length: ' + self.content_length,
            'Content-Type: ' + self.content_type,
            'Connection: close',
            '\r\n',
            self.content,
        ]

        return '\n'.join(out)
