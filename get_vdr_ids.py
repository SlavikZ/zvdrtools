#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
from zvdrtools.vdrtools import get_vdr_channels_conf_reader, get_vdr_channels_custom_dict, get_channel_id

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-d", "--host", action="store", type="string", dest="hostname", default='localhost',
                      help="SVDRP destination hostname (default: localhost)")
    parser.add_option("-p", "--port", action="store", type="int", dest="port", default=6419,
                      help="SVDRP port number (default: 6419)")
    parser.add_option("-f", "--file", action="store", type="string", dest="vdr_channels_file",
                      help="Path to channels.conf file. SVDRP parameters will be ignored")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output with debug info")
    (options, args) = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    channels_conf = get_vdr_channels_conf_reader(options.vdr_channels_file, options.hostname, options.port)
    channels_dict = get_vdr_channels_custom_dict(channels_conf,
                                                 lambda channel: '%s-%s' % (get_channel_id(channel), channel.freq),
                                                 lambda channel: {'name': channel.name, 'id': get_channel_id(channel)}
    )
    for channel in channels_dict.values():
        print "%s=%s" % (channel['name'], channel['id'])
