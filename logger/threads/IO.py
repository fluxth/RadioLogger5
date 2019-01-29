import socket
import os
import threading
import json

from common.utils import Printable
from logger.threads import BaseThread


class IOThread(BaseThread, Printable):

    _tname: str = 'IO'
    _sockfile: str = './rl5.sock'

    sock = None

    def __init__(self):
        super().__init__(self)

    def initialize(self):
        self.name = self._tname

        self.initializeSocket()

        self.info('I/O Thread initialized.')

    def initializeSocket(self):
        self.removeOldSocketFile()

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self._sockfile)
    
        self.sock.listen(1)

    def removeOldSocketFile(self):
        if os.path.exists(self._sockfile):
            os.remove(self._sockfile)

    def run(self):
        self.initialize()

        while not self.exit:
            try:
                conn, addr = self.sock.accept()
                cmd = conn.recv(1024)
                
                if cmd is None:
                    continue

                if len(cmd) <= 0:
                    continue

                cmd = cmd.decode('utf-8')
                result = self.processCommand(cmd)

                if result is not None:
                    conn.sendall(result.encode('utf-8'))

            except OSError as e:
                    if self.exit and e.errno == 9:
                        break

                    raise

            finally:
                conn.close()

    def processCommand(self, cmd, echo=False):
        result = ''

        if cmd == 'quit':
            self._MASTER.shutdown()
            # pass

        elif cmd == 'check':
            wd_status = self._MASTER.checkWatchdogThread(report=echo)
            status = self._MASTER.t_watchdog.checkThreads(report=echo)
            status['watchdog'] = wd_status

            result = status
            
        # elif cmd == 'init':
        #     self.spawnStationThread('Cool93')
        # elif cmd == 'kill':
        #     self.t_stations[0].shutdown()
        # elif cmd == 'kw':
        #     self.t_watchdog.shutdown()
        elif cmd == 'threads':
            print([(t.name, t.ident) for t in threading.enumerate()])

        else:
            print('Unknown Command: {}'.format(cmd))

        return json.dumps(result)

    def shutdown(self):
        if not self.isAlive():
            return

        self.exit = True

        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).connect(self._sockfile)
        self.sock.close()
        self.removeOldSocketFile()

        self.warning('IO shutting down.')
        return self.join()
