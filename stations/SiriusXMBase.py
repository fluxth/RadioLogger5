from logger.station import Station, Metadata
from common.exceptions import StationParseError

import time

'''
Station Template file:

NOTE: your class name MUST be your filename appended by "Station"
eg. 'BaseTemplate.py' -> class BaseTemplateStation(Station)

In order to enable this station, add this station's filename (without .py)
to the rl5's `config.json` file and restart or reload the logger.
'''
class SiriusXMBase(Station):

    _NAME = 'SiriusXM'
    _SHORTNAME = 'SXM'

    _XMCH = ''

    _URL = 'https://player.siriusxm.com/rest/v4/experience/modules/tune/now-playing-live?channelId={ch}&hls_output_mode=none&marker_mode=all_separate_cue_points&ccRequestType=AUDIO_VIDEO&result-template=web&time={XMTS}'

    def initializeStation(self):
        auth_data = {
            "moduleList": {
                "modules": [
                    {
                        "moduleRequest": {
                            "resultTemplate": "web",
                            "deviceInfo": {
                                "appRegion":"US",
                                "language":"en",
                                "browser":"Chrome",
                                "browserVersion":"79.0.3945.130",
                                "clientCapabilities": ["enhancedEDP","seededRadio", "zones","cpColorBackground"],
                                "clientDeviceId": None,
                                "clientDeviceType":"web",
                                "deviceModel":"EverestWebClient",
                                "osVersion":"Windows",
                                "platform":"Web",
                                "player":"html5",
                                "sxmAppVersion":"5.22.3165",
                                "sxmGitHashNumber":"61b1dc5",
                                "sxmTeamCityBuildNumber": "3165",
                                "isChromeBrowser":  True,
                                "isMobile": False,
                                "supportsAddlChannels": True
                            }
                        }
                    }
                ]
            }
        }

        auth = self._session.post('https://player.siriusxm.com/rest/v2/experience/modules/resume?OAtrial=true&cacheBuster={ts}', json=auth_data).json()
        if not auth['ModuleListResponse']['status'] == 1:
            return False

        return True

    def getUrl(self):
        ts = int(time.time()*1000)
        return self._URL.format(XMTS=ts, ch=self._XMCH)

    def parseResponse(self, payload):
        data = payload.json()
        markers = data['ModuleListResponse']['moduleList']['modules'][0]['moduleResponse']['liveChannelData']['markerLists']

        cut_markers = None

        for m in markers[::-1]:
            if m['layer'] == 'cut':
                cut_markers = m['markers']
                break

        if cut_markers is None:
            raise StationParseError('Cut markers not found!')

        for m in cut_markers[::-1]:
            if m['cut']['cutContentType'] == 'Song':
                mts = int(m['time'])
                title = m['cut']['title']
                artists = ', '.join([o['name'] for o in m['cut']['artists']])

                return Metadata(title=title, artist=artists)

        return None

    def isDefaultMetadata(self, metadata):
        # Returns True if the parsed data is the station's default metadata
        return False