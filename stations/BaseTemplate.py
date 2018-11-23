from logger.station import Station, Metadata

'''
Station Template file:

NOTE: your class name MUST be your filename appended by "Station"
eg. 'BaseTemplate.py' -> class BaseTemplateStation(Station)

In order to enable this station, add this station's filename (without .py)
to the rl5's `config.json` file and restart or reload the logger.
'''
class BaseTemplateStation(Station):

    _NAME = 'StationName'
    _SHORTNAME = 'STN'

    _URL = 'https://your-metadata-endpoint/'

    '''
    payload: Request "Response" object
    @return: Metadata object or NoneType
    '''
    def parseResponse(self, payload):
        # Your logic here
        return Metadata(title='', artist='')

    '''
    metadata: Metadata object
    @return: boolean
    '''
    def isDefaultMetadata(self, metadata):
        # Returns True if the parsed data is the station's default metadata
        return False