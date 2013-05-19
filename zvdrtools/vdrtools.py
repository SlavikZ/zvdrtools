# -*- coding: utf8 -*-
"""
VDR related routines
"""
from collections import namedtuple
import logging
import re
from zvdrtools.svdrpsend import SVDRP

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


def get_vdr_channels_custom_dict(channels_conf, dict_key_func, dict_value_func):
    """
    Build custom VDR channels dict
    :param channels_conf: either path to channel.conf or list of channels.conf lines
    :param dict_key_func: function for dict key calculation. Should accept Channel namedtuple as a parameter.
    :param dict_value_func: function for dict value calculation. Should accept Channel namedtuple as a parameter.
    :return: channels dictionary
    """
    channels_dict = {}
    if isinstance(channels_conf, basestring):
        def read_conf_file():
            with open(channels_conf) as fv:
                for (line_no, line) in enumerate(fv, 1):
                    yield (line_no, line.rstrip('\n'))
        channels_conf_reader = read_conf_file
    else:
        def read_conf_list():
            for (line_no, line) in enumerate(channels_conf, 1):
                yield (line_no, line)
        channels_conf_reader = read_conf_list
    current_bouquet = ''

    for (line_no, line) in channels_conf_reader():
        if line.startswith(':'):
            current_bouquet = line[1:]
            continue
        channel = extract_channel_data(line)
        dict_key = dict_key_func(channel)
        dict_value = dict_value_func(channel)
        channels_dict[dict_key] = dict_value
        logger.debug('%s => %s', dict_key, dict_value)
    return channels_dict

def net_get_channel_list(hostname='localhost', port=6419, timeout=10):
    """
    Get VDR channel conf list with Simple VDR Protocol (SVDRP)
    """
    svdrp = SVDRP(hostname=hostname, port=port, timeout=timeout)
    svdrp.start_conversation()
    cmd_result = svdrp.send_command('LSTC')
    svdrp.finish_conversation()
    channels = []
    c_line_re = re.compile(r'(\d+)\s+(.+)')
    for resp_line in cmd_result:
        if resp_line.code != 250:
            #it is not channel info line, just skip it
            continue
        #split out channel number
        m = c_line_re.search(resp_line.text)
        if m:
            channels.append(m.group(2).rstrip('\r\n'))
        else:
            raise ValueError('Invalid SVDR response line: %s' % resp_line)
    return channels
