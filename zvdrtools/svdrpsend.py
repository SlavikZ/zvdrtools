#!/usr/bin/python
# -*- coding: utf8 -*-
import socket
import logging


CRLF = '\r\n'


class SVDRException(Exception):
    pass


class SVDR(object):
    """Base class for network communication with VDR with the Simple VDR Protocol (SVDRP)"""
    def __init__(self, hostname='localhost', port=6419, timeout=10):
        self.logger = logging.getLogger(__name__)
        self.hostname = hostname
        self.port = port
        self.socket = None
        self.sfile = None
        self.timeout = timeout
        self.response = []

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

    def receive_response(self, flag=0):
        self.logger.debug('Getting response...')
        for rline in self.sfile:
            self.logger.debug('Got line %s.', repr(rline))
            self.response.append(rline)
            if rline[3:4] != '-':
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
    svdr = SVDR(hostname=options.hostname, port=options.port)
    svdr.start_conversation()
    cmd_result = svdr.send_command(vdr_command)
    svdr.finish_conversation()
    print ''.join(cmd_result)
