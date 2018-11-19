from logger.station import Station, Metadata

class AtimeBase(Station):
    _NAME = 'ATime'
    _SHORTNAME = 'AT'

    _URL = ''

    def parseResponse(self, payload):
        data = payload.json()

        current = data['now']

        title = str(current['title']).strip()
        artist = str(current['artist']).strip()
        extras = {
            'id': current['id']
        }

        return Metadata(title=title, artist=artist, extraData=extras)

    def isDefaultMetadata(self, metadata):
        if metadata.extraData['id'] == 0:
            return True

        return False