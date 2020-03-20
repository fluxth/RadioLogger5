from logger.station import Station, Metadata

class Cool93Station(Station):
    _NAME = 'Cool93'
    _SHORTNAME = 'C93'

    _URL = 'http://www.coolism.net/radio/dab/nowplaying.php'

    def parseResponse(self, payload):

        data = payload.json()

        entity = data['data']['entities']

        title = entity['song']
        artist = entity['artist']

        return Metadata(title=title, artist=artist)

    def isDefaultMetadata(self, metadata):
        if metadata.title == 'ONAIR' and metadata.artist == 'COOLfahrenheit':
            return True

        return False