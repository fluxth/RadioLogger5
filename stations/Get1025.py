from logger.station import Station, Metadata
from common.exceptions import StationParseError

class Get1025Station(Station):
    _NAME = 'Get1025'
    _SHORTNAME = 'GET'

    _URL = 'http://www.get1025.com/api1025/api_playlist1025.php'

    def parseResponse(self, payload):
        data = payload.json()

        if data['status'] != '200':
            raise StationParseError()

        current = data['entries']['songnow']

        # print(current['type'])

        return Metadata(
            title=str(current['title']).strip(), 
            artist=str(current['artist']).strip()
        )

    def isDefaultMetadata(self, metadata):
        if metadata.title.lower() == 'iLive'.lower() \
        and metadata.artist.lower() == 'Get1025'.lower():
            return True

        return False