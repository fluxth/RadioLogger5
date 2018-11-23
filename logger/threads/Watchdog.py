import threading
import time

from common.utils import Printable
from logger.threads import BaseThread


class WatchdogThread(BaseThread, Printable):

    _MASTER = None
    _REFRESH: int = 1

    _INTERVAL: int = 20

    _tname: str = 'WDOG'

    _lock: threading.Lock = None

    exit: bool = False

    def __init__(self):
        super().__init__(self)
        self._lock = threading.Lock()

        self.name = self._tname

    def run(self):
        self.info('Watchdog enabled.')

        interval = 0
        while not self.exit:
            if interval <= 0:
                self.checkThreads()

                interval = self._INTERVAL
            else:
                interval -= self._REFRESH

            time.sleep(self._REFRESH)

    def checkThreads(self, report=False):
        if not self._MASTER.t_db.isAlive():
            self.error('Database thread died, respawning...')

            with self._lock:
                self._MASTER.initializeDatabaseThread()

            # Log error to database
            self.callDatabase(
                'logError', 
                station=None, 
                sender_name='WDOG[DB]',
                message='Database thread died. Last Uncaught Exception: {}'.format(self.getLastException()[1]),
                details=self.getLastExceptionTraceback()
            )


        else:
            if report is True:
                self.info('Database thread is running normally.')

        for t_station in self._MASTER.t_stations:
            if not t_station.isAlive():
                self.error('Thread {} died, respawning...'.format(t_station.name))

                with self._lock:
                    self._MASTER.spawnStationThread(t_station.station._NAME)

                # Log error to database
                self.callDatabase(
                    'logError', 
                    station=t_station.station, 
                    sender_name='WDOG[{}]'.format(t_station.name),
                    message='Thread {} died. Last Uncaught Exception: {}'.format(
                        t_station.name, self.getLastException()[1]
                    ),
                    details=self.getLastExceptionTraceback()
                )

            else:
                if report is True:
                    self.info('Thread {} is running normally.'.format(t_station.name))

    def shutdown(self):
        if not self.isAlive():
            return

        # clean up

        self.exit = True

        self.warning('Watchdog disabled.')
        return self.join()



