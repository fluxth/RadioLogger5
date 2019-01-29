from threading import Lock
from time import sleep

from common.utils import Printable
from logger.threads import BaseThread


class WatchdogThread(BaseThread, Printable):

    _REFRESH: int = 1
    _INTERVAL: int = 20

    _tname: str = 'WDOG'

    _lock: Lock = None

    def __init__(self):
        super().__init__(self)
        self._lock = Lock()

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

            sleep(self._REFRESH)

    def checkThreads(self, respawn=True, report=False):
        status = {
            'stations': {}
        }

        if not self._MASTER.t_db.isAlive():
            if respawn:
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
                self.error('Database thread died.')

            status['db'] = False
        else:
            if report is True:
                self.info('Database thread is running normally.')

            status['db'] = True
            

        if not self._MASTER.t_io.isAlive():
            if respawn:
                self.error('I/O thread died, respawning...')

                with self._lock:
                    self._MASTER.initializeIOThread()

                # Log error to database
                self.callDatabase(
                    'logError', 
                    station=None, 
                    sender_name='WDOG[IO]',
                    message='IO thread died. Last Uncaught Exception: {}'.format(self.getLastException()[1]),
                    details=self.getLastExceptionTraceback()
                )
            else:
                self.error('I/O thread died.')

            status['io'] = False

        else:
            if report is True:
                self.info('I/O thread is running normally.')

            status['io'] = True


        for t_station in self._MASTER.t_stations:
            if not t_station.isAlive():
                if respawn:
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
                    self.error('Thread {} died.'.format(t_station.name))

                status['stations'][t_station.station._NAME] = False

            else:
                if report is True:
                    self.info('Thread {} is running normally.'.format(t_station.name))

                status['stations'][t_station.station._NAME] = True    

        return status            

    def shutdown(self):
        if not self.isAlive():
            return

        # clean up

        self.exit = True

        self.warning('Watchdog disabled.')
        return self.join()
