from logger.threads import GenericThread
from logger.threads.Database import DatabaseThread
from logger.threads.Station import StationThread
from logger.threads.Watchdog import WatchdogThread
from common.utils import Config, Printable

import sys
import time
import os.path
import logging
from importlib import import_module

import threading


class RadioLogger(GenericThread, Printable):

    _VERSION: str = '5.0.2'
    _MASTER = None

    _REFRESH: int = 1
    _INTERVAL: int = 120

    _tname: str = 'MAIN'

    IS_DAEMON: bool = False
    BASE_DIR: str = None

    config: Config = None

    t_db: DatabaseThread = None
    t_watchdog: WatchdogThread = None
    t_stations: list = []

    def __init__(self):
        self._MASTER = self

    def run(self):
        try:
            self.info('Radio Logger v{} starting...'.format(self._VERSION))

            if self.IS_DAEMON:
                self.info('Running in daemon mode.')

            self.loadConfig(os.path.join(self.BASE_DIR, 'config.json'))
            self.initializeDatabaseThread()
            self.initializeStationThreads()
            self.initializeWatchdogThread()

            self.mainLoop()

        except KeyboardInterrupt:
            self.shutdown(0, 'User quit')

    def mainLoop(self):
        # TODO: Different mainloop for daemon mode
        while True:
            if not self.IS_DAEMON:

                cmd: str = input()

                if cmd == 'quit':
                    raise KeyboardInterrupt
                elif cmd == 'check':
                    self.checkWatchdogThread(report=True)
                    self.t_watchdog.checkThreads(report=True)
                elif cmd == 'init':
                    self.spawnStationThread('Cool93')
                elif cmd == 'kill':
                    self.t_stations[0].shutdown()
                elif cmd == 'kw':
                    self.t_watchdog.shutdown()
                elif cmd == 'threads':
                    print([(t.name, t.ident) for t in threading.enumerate()])
                else:
                    print('Unknown Command')

            else:
                interval = 0

                # Nested loop, avoid having to check for daemon mode every tick.
                while True:
                    if interval <= 0:
                        self.checkWatchdogThread()
                        
                        interval = self._INTERVAL
                    else:
                        interval -= self._REFRESH

                    time.sleep(self._REFRESH)

    def loadConfig(self, path):
        self.config = Config(path)

    def initializeDatabaseThread(self):
        self.t_db = DatabaseThread(self.config.get('database'))
        self.t_db._MASTER = self
        self.t_db.start()

    def initializeStationThreads(self):
        station_list: list = self.config.get('enabled_stations')

        for s in station_list:
            self.spawnStationThread(s)

    def initializeWatchdogThread(self):
        self.t_watchdog = WatchdogThread()
        self.t_watchdog._MASTER = self
        self.t_watchdog.start()

    def checkWatchdogThread(self, report=False):
        if not self.t_watchdog.isAlive():
            self.error('Watchdog thread died, respawning...')

            self.initializeWatchdogThread()

            self.callDatabase(
                'logError', 
                station=None, 
                sender_name='MAIN',
                message='Watchdog thread died. Last Uncaught Exception: {}'.format(
                    self.getLastException()[1]
                ),
                details=self.getLastExceptionTraceback()
            )
        else:
            if report is True:
                self.info('Watchdog thread is running normally.')

    def spawnStationThread(self, station_name):
        s_module = import_module('stations.{}'.format(station_name))
        s_class = getattr(s_module, '{}Station'.format(station_name))

        old_thread_id = None
        for t_station in self.t_stations:
            if type(t_station.station) is s_class:
                if t_station.isAlive():
                    self.warning('Cannot initialize station "{}", it is already running.'.format(
                        s_class.__name__
                    ))
                    return False
                else:
                    self.t_stations.remove(t_station)
                    old_thread_id = t_station._id

        s_thread: StationThread = StationThread(s_class)
        s_thread._MASTER = self
        self.t_stations.append(s_thread)

        if old_thread_id is not None:
            s_thread._id = old_thread_id
        else:
            s_thread._id = len(self.t_stations) - 1

        s_thread.start()

    def shutdown(self, exit_code=0, reason=None):
        if reason is not None:
            self.info('{}, shutdown sequence initiated.'.format(reason))

        if self.t_watchdog is not None:
            self.t_watchdog.shutdown()

        for t_station in self.t_stations:
            if t_station is not None:
                t_station.shutdown()

        if self.t_db is not None:
            self.t_db.shutdown()

        self.warning('Terminating...')
        sys.exit(exit_code)
