#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
from zvdrtools.enigma2tools import get_e2vdr_channels_map
from zvdrtools.epg.xmltvhelper import store_xmltv2vdr_mappings
from zvdrtools.vdrtools import get_vdr_channels_conf_reader, get_vdr_channels_custom_dict, get_channel_id

try:
    from xml.etree.cElementTree import ElementTree, Element, iterparse
except ImportError:
    from xml.etree.ElementTree import ElementTree, Element, iterparse

logger = logging.getLogger(__name__)


def process_linuxsat_mappings(xmltv_channels_file, channels_dict):
    if xmltv_channels_file.endswith('gz'):
        import gzip

        open_func = gzip.open
    else:
        open_func = open
    xmltv_channels_map = {}
    with open_func(xmltv_channels_file) as fp:
        for event, elem in iterparse(fp):
            if elem.tag == 'channel' and len(elem.attrib['id']) > 0:
                elem_service_ref = elem.text.rstrip(':').lower()
                if elem_service_ref in channels_dict:
                    channel = channels_dict[elem_service_ref]
                    xmltv_id = elem.attrib['id']
                    if xmltv_id in xmltv_channels_map:
                        xmltv_channels_map[xmltv_id].append(channel)
                    else:
                        xmltv_channels_map[xmltv_id] = [channel]
                    logger.info('%s (%s) - %s', channel['name'], channel['channel_id'], elem.attrib['id'])
    return xmltv_channels_map


def main():
    from optparse import OptionParser
    usage = "usage: %prog [options]..."
    parser = OptionParser(usage)
    parser.add_option("-d", "--host", action="store", type="string", dest="hostname", default='localhost',
                      help="SVDRP destination hostname (default: localhost)")
    parser.add_option("-p", "--port", action="store", type="int", dest="port", default=6419,
                      help="SVDRP port number (default: 6419)")
    parser.add_option("-f", "--file", action="store", type="string", dest="vdr_channels_file",
                      help="Path to channels.conf file. SVDRP parameters will be ignored")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output with debug info")
    parser.add_option("-x", "--lstv", action="store", type="string", dest="xmltv_channels_file",
                      default='./ua.channels.xml.gz',
                      help="Path to ??.channels.xml.gz file (default: ./ua.channels.xml.gz")
    parser.add_option("-o", "--out", action="store", type="string", dest="xmltv_channels_map_config",
                      default='./channels-map.ini',
                      help="Path to channels-map.ini file (default: ./channels-map.ini")
    parser.add_option("-i", "--id-list", action="store_true", dest="id_list_only",
                      help="show VDR channels ID and exit")
    (options, args) = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    channels_conf = get_vdr_channels_conf_reader(options.vdr_channels_file, options.hostname, options.port)
    if options.id_list_only:
        logger.debug("Show VDR Channels ID only")
        channels_dict = get_vdr_channels_custom_dict(channels_conf,
                                                     lambda channel: '%s-%s' % (get_channel_id(channel), channel.freq),
                                                     lambda channel: {'name': channel.name,
                                                                      'id': get_channel_id(channel)}
        )
        for channel in channels_dict.values():
            print "%s=%s" % (channel['name'], channel['id'])
    else:
        channels_dict = get_e2vdr_channels_map(channels_conf)
        xmltv_channels_map = process_linuxsat_mappings(options.xmltv_channels_file, channels_dict)
        store_xmltv2vdr_mappings(options.xmltv_channels_map_config, xmltv_channels_map)


if __name__ == '__main__':
    main()