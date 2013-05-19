#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import namedtuple
import re
import socket
import logging


CRLF = '\r\n'

Response = namedtuple('Response', 'code delim text')

class SVDRPException(Exception):
    pass


class SVDRP(object):
    """Base class for network communication with VDR with the Simple VDR Protocol (SVDRP)"""
    def __init__(self, hostname='localhost', port=6419, timeout=10):
        self.logger = logging.getLogger(__name__)
        self.hostname = hostname
        self.port = port
        self.socket = None
        self.sfile = None
        self.timeout = timeout
        self.response = []
        response_pat = r'^(\d+)(\s|-)(.+)$'
        self.response_re = re.compile(response_pat)

    def start_conversation(self):
        self.response = []
        self.logger.debug('Start conversation with %s:%s.', self.hostname, self.port)
        self.socket = socket.create_connection((self.hostname, self.port), self.timeout)
        self.sfile = self.socket.makefile('r')
        self.receive_response()

    def finish_conversation(self):
        self.logger.debug('Finish conversation with %s:%s.', self.hostname, self.port)
        self.send_command('quit')
        self.sfile.close()
        self.socket.close()
        self.sfile = self.socket = None

    def send(self, cmd):
        self.logger.debug('Send %s to host', repr(cmd))
        self.socket.sendall(cmd + CRLF)

    def send_command(self, cmd):
        self.send(cmd)
        self.receive_response()
        return self.response

    def parse_response(self, response_str):
        m = self.response_re.search(response_str)
        if m:
            return Response(int(m.group(1)), m.group(2), m.group(3))
        else:
            raise ValueError('Invalid response: %s' % response_str)

    def receive_response(self, flag=0):
        self.logger.debug('Getting response...')
        for rline in self.sfile:
            self.logger.debug('Got line %s.', repr(rline))
            resp = self.parse_response(rline)
            self.response.append(resp)
            if resp.delim != '-':
                #no more lines expected
                break
        else:
            self.logger.debug('Empty response.')
        self.logger.debug('Got response.')
        return self.response


if __name__ == '__main__':
    from optparse import OptionParser
    usage = "usage: %prog [options] command..."
    parser = OptionParser(usage)
    parser.add_option("-d", "--host", action="store", type="string", dest="hostname", default='localhost',
        help="destination hostname (default: localhost)")
    parser.add_option("-p", "--port", action="store", type="int", dest="port", default=6419,
        help="SVDRP port number (default: 6419)")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="verbose output with debug info")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("missing command")
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    vdr_command = " ".join(args)
    logging.debug('Command: %s', vdr_command)
    svdrp = SVDRP(hostname=options.hostname, port=options.port)
    svdrp.start_conversation()
    cmd_result = svdrp.send_command(vdr_command)
    svdrp.finish_conversation()
    for resp_line in cmd_result:
        print '%s%s%s' % (resp_line.code, resp_line.delim, resp_line.text)
