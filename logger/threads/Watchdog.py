import threading
import time

from common.utils import Printable


class WatchdogThread(threading.Thread, Printable):

    _MASTER = None
    _REFRESH = 1

    _INTERVAL = 20

    _tname = 'WDOG'

    _lock: threading.Lock = None

    exit = False

    def __init__(self):
        threading.Thread.__init__(self)
        self._lock = threading.Lock()

    def run(self):
        self.print('Watchdog enabled.')

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

        else:
            if report is True:
                self.print('Database thread is running normally.')

        for t_station in self._MASTER.t_stations:
            if not t_station.isAlive():
                self.error('Thread {} died, respawning...'.format(t_station.name))
                with self._lock:
                    self._MASTER.spawnStationThread(t_station.station._NAME)
            else:
                if report is True:
                    self.print('Thread {} is running normally.'.format(t_station.name))

    def shutdown(self):
        if not self.isAlive():
            return

        # clean up

        self.exit = True

        self.warning('Watchdog disabled.')
        return self.join()



