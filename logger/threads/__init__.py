import threading
import sys
import traceback

from logger.actions import DatabaseAction

class GenericThread():
    _MASTER = None
    
    def callDatabase(self, method, *args, **kwargs):
        if not self._MASTER.t_db.isAlive():
            self.error('"db.{}" not avaliable, Database thread is not running.'.format(method))
            return

        action = DatabaseAction()
        action.method = method
        action.args = args
        action.kwargs = kwargs

        self._MASTER.t_db.q.put(action)

    def getLastException(self):
        try:
            return (sys.last_type, sys.last_value, sys.last_traceback)
        except AttributeError:
            return (None, None, None)

    def getLastExceptionTraceback(self):
        lt, lv, ltb = self.getLastException()

        if lt is None:
            return None

        tb = traceback.format_exception(lt, lv, ltb)
        return ''.join(tb)

class BaseThread(GenericThread, threading.Thread):

    _tname: str = 'thread'

    exit: bool = False

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)

    def shutdown(self):
        if not self.isAlive():
            return

        self.exit = True
        return self.join()
