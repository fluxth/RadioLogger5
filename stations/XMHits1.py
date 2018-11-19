from logger.station import Station, Metadata
from common.exceptions import StationParseError

import datetime

class XMHits1Station(Station):
    _NAME = 'XMHits1'
    _SHORTNAME = 'XM1'

    _URL = 'https://www.siriusxm.com/metadata/pdt/en-us/json/channels/siriushits1/timestamp/{XMTS}'

    def getUrl(self):
        dt = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        ts = '{d.month:02}-{d.day:02}-{d.hour:02}:{d.minute:02}:00'.format(d=dt)
        return self._URL.format(XMTS=ts)

    def parseResponse(self, payload):
        data = payload.json()

        resp = data['channelMetadataResponse']
        
        if resp['messages']['code'] != 100:
            return None

        current = resp['metaData']['currentEvent']

        title = str(current['song']['name']).strip()
        artist = str(current['artists']['name']).strip()

        return Metadata(title=title, artist=artist)

    def isDefaultMetadata(self, metadata):
        # TODO
        keywords = [
            'SiriusXM',
            'Hits1',
            'MorningMashUp'
        ]

        if any(kw.lower() in metadata.title.lower() for kw in keywords) \
        or any(kw.lower() in metadata.artist.lower() for kw in keywords):
            return True

        return False