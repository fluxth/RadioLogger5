from requests import Request, Session
from requests.exceptions import RequestException
from datetime import datetime
from json.decoder import JSONDecodeError

from common.exceptions import StationParseError

import abc


class Station(object):

    _THREAD = None

    _NAME: str = 'Station'
    _SHORTNAME: str = 'ST'

    _INTERVAL: int = 60

    _URL: str = None
    _POSTDATA = None
    _TIMEOUT: int = 10

    _session: Session = None
    _headers: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.initializeRequests()

    def initializeRequests(self):
        self._session = Session()

    def httpGet(self, url):
        req = Request('GET', url, headers=self._headers)
        prepped = self._session.prepare_request(req)
        return self._session.send(prepped, timeout=self._TIMEOUT)

    def httpPost(self, url, data = {}):
        req = Request('POST', url, data=data, headers=self._headers)
        prepped = self._session.prepare_request(req)
        return self._session.send(prepped, timeout=self._TIMEOUT)

    def getUrl(self):
        return self._URL

    def requestMetadata(self):
        if self.getUrl is None:
            raise NotImplementedError('<{}> URL is not specified.'.format(
            self.__class__.__name__
        ))

        data = None

        try:
            if self._POSTDATA is None:
                data = self.httpGet(self.getUrl())
            else:
                data = self.httpPost(self.getUrl(), self._POSTDATA)
            
        except RequestException as e:
            self._THREAD.error('Error while fetching: {}'.format(e))

            # Log error to database
            self._THREAD.callDatabase(
                'logError', 
                station=self, 
                sender_name=self._THREAD.name,
                message='Handled RequestException: {}'.format(e),
                details='ReqURL = {}'.format(e.request.url if e.request is not None else 'None')
            )

            return None

        try:

            metadata = self.parseResponse(data)

        except JSONDecodeError as e:
            self._THREAD.error('Error parsing JSON: {}'.format(e))

            # Log error to database
            self._THREAD.callDatabase(
                'logError', 
                station=self, 
                sender_name=self._THREAD.name,
                message='Handled JsonDecodeError: {}'.format(e),
                # details=e.doc
                # TODO: Log corrupted json file to disk
            )

            return None

        except StationParseError as e:
            self._THREAD.error('Error parsing metadata: {}'.format(e))

            # Log error to database
            self._THREAD.callDatabase(
                'logError', 
                station=self, 
                sender_name=self._THREAD.name,
                message='Handled StationParseError: {}'.format(e),
                # details=e.doc
                # TODO: Log parse error w/ file to disk
            )

            return None


        if metadata is None:
            return None

        if self.isDefaultMetadata(metadata) is True:
            metadata.isDefault = True

        return metadata

    def check(self):
        # add duplicates check
        metadata = self.requestMetadata()

        return metadata

    @abc.abstractmethod
    def parseResponse(self, payload):
        # Returns Metadata object
        raise NotImplementedError('<{}> ParseResponse not implemented.'.format(
            self.__class__.__name__
        ))

    def isDefaultMetadata(self, metadata):
        # Returns True if the parsed data is the station's default metadata
        return False


class Metadata(object):

    isDefault = False

    title = None
    artist = None

    timestamp = None

    extraData = None

    def __init__(self, title=None, artist=None, default=False, extraData=None):
        if not default:
            if title is None or artist is None:
                raise ValueError('Title and Artist cannot be NoneType')

        self.title = title
        self.artist = artist
        self.isDefault = default
        self.extraData = extraData
        self.timestamp = datetime.utcnow()

    def __str__(self):
        if self.isDefault:
            return '<Default>'
        return '<"{}" - "{}">'.format(self.artist, self.title)

    def __repr__(self):
        if self.isDefault:
            return '<Metadata default=True>'
        return '<Metadata title={} artist={}>'.format(self.title, self.artist)




