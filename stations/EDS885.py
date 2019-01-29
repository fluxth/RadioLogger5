from logger.station import Station, Metadata
from common.exceptions import StationParseError

import defusedxml.ElementTree as et

class EDS885Station(Station):
    _NAME = 'EDS885'
    _SHORTNAME = 'EDS'

    _URL = 'http://www.everydaystation.com/billboard'

    def extractFromXml(self, xml):
        title = None
        artists = []
        extras = {}

        event = xml[0]
        for media in event:
            if media.tag == '{urn:schemas-rcsworks-com:SongSchema}Song':
                title = media.attrib['title'].strip()

                extras['id'] = media.attrib['ID'].strip()
                extras['category'] = media.attrib['category'].strip()

                for detail in media:
                    if detail.tag == '{urn:schemas-rcsworks-com:SongSchema}Artist':
                        artists.append(detail.attrib['name'].strip())

                return Metadata(title=title, artist='/'.join(artists), extraData=extras)

            # Check if there is another Link after this occurrance
            elif media.tag == '{urn:schemas-rcsworks-com:SongSchema}Link':
                if len(xml) > 1:
                    next_event = xml[1]

                    for next_media in next_event:
                        if next_media.tag == '{urn:schemas-rcsworks-com:SongSchema}Link':
                            return Metadata(default=True)

    def parseResponse(self, payload):
        data = payload.content.decode('tis-620')

        if len(data.strip()) <= 0:
            return None

        try:
            xml = et.fromstring(data)
            metadata = self.extractFromXml(xml)
        except TypeError:
            return None

        return metadata

    def isDefaultMetadata(self, metadata):
        # TODO
        if metadata.title == '' and metadata.artist == '':
            return True

        return False
