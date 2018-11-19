from logger.station import Station, Metadata

class Cool93Station(Station):
    _NAME = 'Cool93'
    _SHORTNAME = 'C93'

    _URL = 'http://www.coolism.net/mobile-xml/fahrenheit/rcs/BILLBOARD.ASC'

    def parseResponse(self, payload):
        track = payload.content.decode('tis-620').split('\r\n')[0]

        try:
            title = track[:50].strip()
        except IndexError:
            title = ''

        try:
            artist = track[50:80].strip().replace('_', ' ')
        except IndexError:
            artist = ''

        return Metadata(title=title, artist=artist)

    def isDefaultMetadata(self, metadata):
        if metadata.title == '' and metadata.artist == '':
            return True

        return False