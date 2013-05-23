#!/usr/bin/python
# -*- coding: utf8 -*-
"""
XMLTV <-> VDR EPG conversion routines
"""
from datetime import timedelta, datetime
import calendar
import logging
import xmltv

try:
    from xml.etree.cElementTree import ElementTree, Element, iterparse
except ImportError:
    from xml.etree.ElementTree import ElementTree, Element, iterparse

MAP_SECTION = 'Mappings'
logger = logging.getLogger(__name__)


def get_timestamp_utc_now():
    """
    Return current time in UNIX timestamp format
    (number of seconds since 00:00:00 UTC on January 1, 1970)
    """
    return calendar.timegm(datetime.utcnow().utctimetuple())


def store_xmltv2vdr_mappings(xmltv_channels_map_config, xmltv_channels_map):
    """
    Store XMLTV to VDR channels mapping to config file
    """
    import ConfigParser
    if len(xmltv_channels_map) > 0:
        config = ConfigParser.ConfigParser()
        config.read(xmltv_channels_map_config)

        try:
            config.remove_section(MAP_SECTION)
        except ConfigParser.NoSectionError:
            pass
        config.add_section(MAP_SECTION)
        for map_id, map_item in sorted(xmltv_channels_map.iteritems()):
            #store additional information as a comment
            item_comment = '; '.join(['%s=%s' % (item['channel_id'], item['name']) for item in map_item])
            config.set(MAP_SECTION, ';' + item_comment, '')
            #store the item itself
            item_value = ','.join([item['channel_id'] for item in map_item])
            config.set(MAP_SECTION, map_id, item_value)
        with open(xmltv_channels_map_config, 'wb') as configfile:
            config.write(configfile)


def read_xmltv2vdr_mappings(xmltv_channels_map_config, channels_dict):
    """
    Read XMLTV to VDR channels mapping and check VDR Channels IDs existence in provided channels_dict
    Return map dictionary in {<XMLTV_ID>: {'id': <VDR Channel ID>, 'name': <VDR Channel Name>}} format
    """
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(xmltv_channels_map_config)

    channels_map = {}
    for opt in config.options(MAP_SECTION):
        map_channels_id = [{'id': c, 'name': channels_dict[c]}
                           for c in config.get(MAP_SECTION, opt).split(',') if c in channels_dict]
        if map_channels_id:
            channels_map[opt] = map_channels_id
        else:
            logger.warning('For mapping rule <%s> there are no available any VDR channels. Refresh your mapping file.', opt)
    return channels_map

class XMLTV:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tree = ElementTree()
        self._tree._setroot(Element('tv'))
        self._loaded_channels = []

    def get_loaded_channels(self):
        return self._loaded_channels

    def parse_xmltv_file(self, filename, channel_list):
        """
        Process given xmltv file and create xml tree for our channel_list
        """
        self.logger.debug("Start <%s> parsing>", filename)
        if filename.endswith('gz'):
            import gzip
            open_func = gzip.open
        else:
            open_func = open
        with open_func(filename) as fp:
            for event, elem in iterparse(fp):
                if elem.tag == 'channel':
                    if elem.attrib['id'] in channel_list:
                        self.logger.debug("Add <%s> channel element", elem.attrib['id'])
                        self._tree.getroot().append(elem)
                        if elem.attrib['id'] not in self._loaded_channels:
                            self._loaded_channels.append(elem.attrib['id'])
                    else:
                        elem.clear()
                elif elem.tag == 'programme':
                    if elem.attrib['channel'] in channel_list:
                        self._tree.getroot().append(elem)
                    else:
                        elem.clear()
        self.logger.debug('File parsing complete!')

    @classmethod
    def parse_date_tz(cls, date_str):
        """
        Parse date like this: '20130429073000 +0300'
        (python libs unable to process timezone info in +0300 format)
        Most code was taken from email.util package
        :return: parsed datetime object
        """
        tz = date_str[-5:]
        date_str_notz = date_str[:-6]
        tz_offset = int(tz)
        # Convert a timezone offset into seconds ; -0500 -> -18000
        if tz_offset:
            if tz_offset < 0:
                tz_sign = -1
                tz_offset = -tz_offset
            else:
                tz_sign = 1
            tz_offset = tz_sign * ((tz_offset // 100) * 3600 + (tz_offset % 100) * 60)
        time = datetime.strptime(date_str_notz, xmltv.date_format_notz)
        delta = timedelta(seconds=tz_offset)
        time -= delta
        return time

    def parse_programme(self, elem):
        """
        Convert programme element to dictionary
        """
        programme = xmltv.elem_to_programme(elem)
        programme['start_timestamp'] = calendar.timegm(XMLTV.parse_date_tz(programme['start']).utctimetuple())
        programme['stop_timestamp'] = calendar.timegm(XMLTV.parse_date_tz(programme['stop']).utctimetuple())
        self.logger.debug("Programme: %s", programme)
        return programme

    def get_tv_schedule(self, channel_name=None):
        """
        Get generator object for tv schedule of given channel_name or for all loaded channels
        """
        if channel_name is not None:
            filter_str = 'programme[@channel="%s"]' % channel_name
        else:
            filter_str = 'programme'
        for elem in self._tree.findall(filter_str):
            yield self.parse_programme(elem)
