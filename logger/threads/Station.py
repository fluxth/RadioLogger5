import time

from common.utils import Printable
from logger.threads import BaseThread


class StationThread(BaseThread, Printable):

    _MASTER = None
    _REFRESH: int = 1

    _tname: str = '#'
    _id = None

    station = None
    _stationclass = None

    exit: bool = False

    def __init__(self, station_class):
        super().__init__(self)

        self._stationclass = station_class

    def initialize(self):
        self.station = self._stationclass()
        self._stationclass = None

        self.station._THREAD = self

        self._tname = '{}#{}'.format(self._id, self.station._SHORTNAME)
        self.name = self._tname

        self.callDatabase('registerStation', station=self.station)

        self.info('Logger started.')

    def run(self):
        self.initialize()

        interval = 0
        try:

            while not self.exit:
                if interval <= 0:
                    # Do stuff
                    metadata = self.station.check()

                    if metadata is not None:
                        if not self.exit:
                            self.debug(metadata)
                            self.callDatabase('logPlay', station=self.station, metadata=metadata)

                    interval = self.station._INTERVAL
                else:
                    interval -= self._REFRESH

                time.sleep(self._REFRESH)

        except Exception as e:
            self.callDatabase(
                'logError', 
                station=None, 
                sender_name='WDOG[DB]',
                message='Database thread died. Last Uncaught Exception: {}'.format(self.getLastException()[1]),
                details=self.getLastExceptionTraceback()
            )

            raise

    def shutdown(self):
        if not self.isAlive():
            return

        # clean up

        self.exit = True

        self.warning('Logger shutting down.')
        #return self.join()
