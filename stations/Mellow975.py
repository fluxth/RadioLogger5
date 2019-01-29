from logger.station import Station, Metadata
from common.exceptions import StationParseError

class Mellow975Station(Station):
    _NAME = 'Mellow975'
    _SHORTNAME = 'MLW'

    _URL = 'https://mellow975.mcot.net/api/current-next-songs'

    def parseResponse(self, payload):
        data = payload.json()

        if data['status'] != 'ok':
            raise StationParseError('Endpoint returned unknown status', data['status'])

        current = data['data'][0]

        return Metadata(
            title=str(current['song']).strip(), 
            artist=str(current['artist']).strip(),
            extraData={
            	'id': current['id']
            }
        )

    def isDefaultMetadata(self, metadata):
        if len(metadata.title) == 0 and len(metadata.artist) == 0:
            return True

        return False