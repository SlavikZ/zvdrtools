# -*- coding: utf8 -*-
"""
VDR related routines
"""
from collections import namedtuple
import logging

logger = logging.getLogger(__name__)
Channel = namedtuple('Channel', 'name, provider, freq, parameters, source, symbolrate,'
                                ' vpid, apid, tpid, caid, sid, nid, tid, rid')
ChannelSource = namedtuple('ChannelSource', 'type degree origin')


def extract_channel_data(channel_line):
    """
    Extract channel parameters from given channel.conf file line
    :return: Channel namedtuple
    """
    #(name;provider, freq, parameters, source, symbolrate, vpid, apid, tpid, caid, sid, nid, tid, rid)
    logger.debug('Extract channel data for line: %s', channel_line)
    attrs_list = channel_line.split(':')
    names = attrs_list[0].split(';', 2)
    channel_name = names[0]
    if len(names) == 2:
        provider = names[1]
    else:
        provider = ''
    channel = Channel(channel_name,
                      provider,
                      int(attrs_list[1]),
                      attrs_list[2],
                      attrs_list[3],
                      int(attrs_list[4]),
                      attrs_list[5],
                      attrs_list[6],
                      attrs_list[7],
                      attrs_list[8],
                      int(attrs_list[9]),
                      int(attrs_list[10]),
                      int(attrs_list[11]),
                      int(attrs_list[12])
    )
    logger.debug('Extracted: %s', channel)
    return  channel


def get_channel_id(channel_data):
    """
    From given Channel namedtuple return VDR Channel ID string
    (like this: S4.0W-1-20-11)
    """
    #Source (S19.2E), NID (1), TID (1089), SID (12003) and RID
    logger.debug('Getting Channel ID for %s', channel_data)
    channel_id = '%(source)s-%(nid)d-%(tid)d-%(sid)d' % {'source': channel_data.source,
                                                         'nid': channel_data.nid,
                                                         'tid': channel_data.tid,
                                                         'sid': channel_data.sid}
    if channel_data.rid != 0:
        channel_id = "%s-%d" % channel_data.rid
    logger.debug('Channel ID=%s', channel_id)
    return channel_id


def get_polarisation(channel_parameters):
    """
    Extract polarisation character (L R V H) from VDR channel parameters string
    """
    return next(s.upper() for s in channel_parameters if s in 'HhVvRrLl')
