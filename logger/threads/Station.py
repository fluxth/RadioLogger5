import threading
import time

from common.utils import Printable
from logger.actions import DatabaseAction


class StationThread(threading.Thread, Printable):

    _MASTER = None
    _REFRESH = 1

    _tname = '#'
    _id = None

    station = None
    _stationclass = None

    exit = False

    def __init__(self, station_class):
        threading.Thread.__init__(self)

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

    def callDatabase(self, method, *args, **kwargs):
        if not self._MASTER.t_db.isAlive():
            self.error('Cannot save metadata, Database thread is not running.')
            return

        action = DatabaseAction()
        action.method = method
        action.args = args
        action.kwargs = kwargs

        self._MASTER.t_db.q.put(action)

    def shutdown(self):
        if not self.isAlive():
            return

        # clean up

        self.exit = True

        self.warning('Logger shutting down.')
        #return self.join()
