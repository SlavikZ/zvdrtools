#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging
import os
import re
from zvdrtools.enigma2tools import get_enigma2_service_reference
from zvdrtools.vdrtools import get_vdr_channels_conf_reader, get_vdr_channels_custom_dict, get_channel_id


logger = logging.getLogger(__name__)
OCRAM_SH_REGEXP = r'^\s*ln\s+-s\s+(\S+)\s+(\S+)\.uid\s*$'

def get_ocram_channel_id(channel):
    e2_service_ref = get_enigma2_service_reference(channel)
    e2_service_ref_parts = e2_service_ref.split(':')
    if e2_service_ref_parts[2] == '2':
        service_type = 'radio'
    else:
        service_type = 'tv'
    short_channel_id = '_'.join(e2_service_ref_parts[3:-3]).upper()
    ocram_channel_id = '%s.%s' % (service_type, short_channel_id)
    return ocram_channel_id

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
    parser.add_option("-i", "--ocram_file", action="store", type="string", dest="ocram_sh_file", default='./picons.sh',
                      help="Path to ocram's picons.sh file (default: ./picons.sh)")
    parser.add_option("--out_mask", action="store", type="string", dest="out_mask", default='%(ocram_name)s - %(vdr_name)s',
                      help="Output print mask. You may use the following named parameters: 'ocram_name', 'vdr_name'"
                           ", 'vdr_id'. Default value: '%(ocram_name)s - %(vdr_name)s')")
    (options, args) = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    #read our VDR channels
    channels_conf = get_vdr_channels_conf_reader(options.vdr_channels_file, options.hostname, options.port)
    channels_dict = get_vdr_channels_custom_dict(channels_conf, get_ocram_channel_id,
                                                 lambda channel: {'name': channel.name,
                                                                  'channel_id': get_channel_id(channel)}
    )

    #process ocram picons.sh file
    ocram_re = re.compile(OCRAM_SH_REGEXP)
    ocram_map = dict()
    with open(options.ocram_sh_file) as ocram_sh_file:
        for sh_line in ocram_sh_file:
            match = re.match(ocram_re, sh_line)
            if match and match.group(2) in channels_dict:
                ocram_file_name, ocram_file_ext = os.path.splitext(match.group(1))
                ocram_map[match.group(1)] = dict(channels_dict[match.group(2)].items()+
                                                 {'ocram_file_name': ocram_file_name,
                                                  'ocram_file_ext': ocram_file_ext}.items())

    #dump results
    for channel in ocram_map:
        print options.out_mask % {'ocram_name' : channel,
                                  'ocram_file_name': ocram_map[channel]['ocram_file_name'],
                                  'ocram_file_ext': ocram_map[channel]['ocram_file_ext'],
                                  'vdr_name' : ocram_map[channel]['name'],
                                  'vdr_id' : ocram_map[channel]['channel_id']
        }
