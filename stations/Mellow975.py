from logger.station import Station, Metadata
from common.exceptions import StationParseError

class Mellow975Station(Station):
    _NAME = 'Mellow975'
    _SHORTNAME = 'MLW'

    _URL = 'https://mellow975.mcot.net/fetch/currentSong'

    def parseResponse(self, payload):
        data = payload.json()
        playlist = data['list']

        for item in playlist[::-1]:
            if item['status'] == 'current':
                return Metadata(
                    title=str(item['song']).strip(), 
                    artist=str(item['artist']).strip(),
                )

        return None

    def isDefaultMetadata(self, metadata):
        if len(metadata.title) == 0 and len(metadata.artist) == 0:
            return True

        return False