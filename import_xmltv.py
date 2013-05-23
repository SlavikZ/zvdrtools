#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
from datetime import datetime
from zvdrtools.epg.xmltvhelper import XMLTV, read_xmltv2vdr_mappings
from zvdrtools.svdrpsend import SVDRP
from zvdrtools.vdrtools import get_vdr_channels_custom_dict, get_channel_id, get_vdr_channels_conf_reader

logger = logging.getLogger(__name__)


def get_vdr_channels_map(channels_conf):
    return get_vdr_channels_custom_dict(channels_conf, get_channel_id, lambda channel: channel.name)


def main():
    from optparse import OptionParser
    usage = "usage: %prog [options]..."
    parser = OptionParser(usage)
    parser.add_option("-d", "--host", action="store", type="string", dest="hostname", default='localhost',
                      help="SVDRP destination hostname (default: localhost)")
    parser.add_option("-p", "--port", action="store", type="int", dest="port", default=6419,
                      help="SVDRP port number (default: 6419)")
    parser.add_option("-f", "--file", action="store", type="string", dest="vdr_channels_file",
                      help="Path to channels.conf file. Channels wil be read from given channels.conf file.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output with debug info")
    parser.add_option("-x", "--xmltv", action="store", type="string", dest="xmltv_filename",
                      default='./tvprogram_ua_ru.gz',
                      help="Path to XMLTV file (default: ./tvprogram_ua_ru.gz)")
    parser.add_option("-o", "--out", action="store", type="string", dest="xmltv_channels_map_config",
                      default='./channels-map.ini',
                      help="Path to channels-map.ini file (default: ./channels-map.ini")
    parser.add_option("-t", "--debug-dump", action="store", type="string", dest="debug_dump",
                      help="Debug dry mode - dump all commands to file, no actual commands send to host")
    (options, args) = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    channels_conf = get_vdr_channels_conf_reader(options.vdr_channels_file, options.hostname, options.port)
    channels_dict = get_vdr_channels_custom_dict(channels_conf, get_channel_id, lambda channel: channel.name)
    channels_map = read_xmltv2vdr_mappings(options.xmltv_channels_map_config, channels_dict)
    svdrp = SVDRP(hostname=options.hostname, port=options.port, debug_dump=options.debug_dump)
    xmltv_handler = XMLTV()
    xmltv_handler.parse_xmltv_file(options.xmltv_filename, channels_map)
    xmltv_handler.process_tv_schedule(channels_map, svdrp)


if __name__ == '__main__':
    main()
