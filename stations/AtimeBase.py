from logger.station import Station, Metadata

class AtimeBase(Station):
    _NAME = 'ATime'
    _SHORTNAME = 'AT'

    _STID = ''

    _URL = 'https://graph.atimeonline.com/v5.0/{station_id}/playing'

    def getUrl(self):
        return self._URL.format(station_id=self._STID)

    def parseResponse(self, payload):
        data = payload.json()

        current = data['data']['audio']

        title = str(current['title']).strip()
        artist = str(current['description']).strip()
        extras = {
            'id': current['id']
        }

        return Metadata(title=title, artist=artist, extraData=extras)

    def isDefaultMetadata(self, metadata):
        if int(metadata.extraData['id']) == 999999:
            return True

        return False