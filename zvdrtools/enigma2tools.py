# -*- coding: utf8 -*-
"""
Enigma2 related routines
Info used:
- OpenPLi (http://openpli.org/) 3.0.6 source code
- GitHub repositories:
-- https://github.com/pipelka/vdr-plugin-xvdr
-- https://github.com/tkurbad/piconscripts
-- https://github.com/k2s/enigma2-php
"""
from decimal import Decimal
import logging
from zvdrtools.vdrtools import ChannelSource, get_polarisation, get_channel_id, get_vdr_channels_custom_dict

logger = logging.getLogger(__name__)

DVB_POLARISATION_FLAG_MAP = {'H': 0,
                             'V': 1,
                             'L': 2,
                             'R': 3}


def enigma2_is_valid_ONID_TSID(onid, tsid, degree):
    """
    Define if ONID/TSID data is valid or not
    Ported from OpenPLi
    """
    orbital_position = int(degree*10)
    if onid == 0 or onid == 0x1111:
        return False
    elif onid == 1:
        return orbital_position == 192
    elif onid == 0x00B1:
        return tsid != 0x00B0
    elif onid == 0x0002:
        return abs(orbital_position-282) < 6
    else:
        return onid < 0xFF00


def get_enigma2_service_reference(channel_data):
    """
    Calculate Enigma2 DVB service reference string from channel data
    (like this: 1:0:1:5:14:1:de82a36:0:0:0)
    """
    logger.debug('Getting Enigma 2 ServiceRef for %s', channel_data)
    sat_hash = freq_hash = 0
    stream_type = 1
    if channel_data.vpid in ('0', '1'):
        stream_type = 2
    elif '=' in channel_data.vpid:
        (pid, video_mode) = [x.strip() for x in channel_data.vpid.split('=')]

        if video_mode == '2':
            stream_type = 1
        #TODO try to understand what is that?
        # Doesn't work good for me
        #if video_mode == '27':
        #    stream_type = 0x19

    if channel_data.source.startswith('S'):
        sat_source = ChannelSource(channel_data.source[0], Decimal(channel_data.source[1:-1]), channel_data.source[-1])
        if sat_source .origin == 'W':
            #enigma2 uses a 3600 east/west origin for the namespace
            sat_hash = int(3600 - sat_source.degree*10)
        else:
            sat_hash = int(sat_source.degree*10)
        # on invalid ONIDs, build hash from frequency and polarisation
        if not enigma2_is_valid_ONID_TSID(channel_data.nid, channel_data.tid, sat_source.degree):
            pol = DVB_POLARISATION_FLAG_MAP[get_polarisation(channel_data.parameters)]
            freq_hash = (channel_data.freq & 0xFFFF) | ((pol & 1) << 15)
    elif channel_data.source.startswith('C'):
        sat_hash = 0xFFFF
    elif channel_data.source.startswith('T'):
        sat_hash = 0xEEEE
    elif channel_data.source.startswith('A'):
        sat_hash = 0xDDDD
    namespace = (sat_hash << 16) | freq_hash
    #TODO explore 1:0 prefix and 0:0:0 suffix
    service_ref = '1:0:%x:%x:%x:%x:%x:0:0:0' % (stream_type, channel_data.sid, channel_data.tid, channel_data.nid, namespace)
    logger.debug('Enigma 2 ServiceRef is: %s', service_ref)
    return service_ref


def get_e2vdr_channels_map(channels_conf):
    def get_dict_value(channel):
        channel_id = get_channel_id(channel)
        return {'name': channel.name, 'channel_id': channel_id}
    return get_vdr_channels_custom_dict(channels_conf, get_enigma2_service_reference, get_dict_value)