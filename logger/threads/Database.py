from queue import Queue

from common.utils import Printable
from logger.threads import BaseThread
from logger.database import Database
from logger.actions import DatabaseAction


class DatabaseThread(BaseThread, Printable):

    _tname: str = 'DB'
    _config: dict = {}

    q: Queue = None
    db: Database = None

    def __init__(self, config):
        super().__init__(self)
        self._config = config
        self.q = Queue()

    def initialize(self):
        self.name = self._tname
        self.db = Database(self._config)
        self.db._THREAD = self

        self.db.initialize()
        self.info('Database initialized.')

    def run(self):
        self.initialize()

        while not self.exit:
            action = self.q.get()
            
            if action is None:
                continue

            if type(action) is DatabaseAction:
                if hasattr(self.db, action.method):
                    getattr(self.db, action.method)(*action.args, **action.kwargs)
                else:
                    self.error('Action method invalid: {}'.format(action.method))
                    continue
            else:
                self.error('Action unknown: {}'.format(action))
                continue

    def shutdown(self):
        if not self.isAlive():
            return
            
        # clean up connection
        self.db.shutdown()

        self.exit = True
        self.q.put(None)

        self.warning('Database shutting down.')
        return self.join()
