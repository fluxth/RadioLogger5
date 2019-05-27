class Tool(object):

    config = None
    db = None

    def __init__(self, config, db):
        self.config = config
        self.db = db

    def _default(self):
        print('{} called.'.format(self.__class__.__name__))