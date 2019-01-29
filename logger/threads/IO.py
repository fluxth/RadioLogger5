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
        error = None

        if cmd == 'quit':
            self._MASTER.shutdown()
            # pass

        elif cmd == 'check' or cmd == 'status':
            respawn = True
            if cmd == 'status':
                respawn = False

            wd_status = self._MASTER.checkWatchdogThread(report=echo, respawn=respawn)
            status = self._MASTER.t_watchdog.checkThreads(report=echo, respawn=respawn)
            status['watchdog'] = wd_status

            result = status
            
        elif cmd == 'threads':
            threads = [
                {
                    'name': t.name, 
                    'ident': t.ident,
                    'alive': t.is_alive()
                } for t in threading.enumerate()
            ]

            if echo:
                for t in threads:
                    print('Thread ID={} [{}] / isAlive: {}'.format(t['ident'], t['name'], t['alive']))

            result = threads

        else:
            error = 'Unknown Command: {}'.format(cmd)

        if error is not None:
            self.warning(error)
            return json.dumps({
                'status': 'error',
                'message': error 
            }, separators=(',',':'))

        return json.dumps({
            'status': 'ok',
            'data': result
        }, separators=(',',':'))

    def shutdown(self):
        if not self.isAlive():
            return

        self.exit = True

        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).connect(self._sockfile)
        self.sock.close()
        self.removeOldSocketFile()

        self.warning('I/O shutting down.')
        return self.join()
