import os.path
import logging
from sys import argv
from threading import get_ident
from daemonize import Daemonize

from logger.controller import RadioLogger


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ih = logging.FileHandler(os.path.join(BASE_DIR, 'rl5.log'), 'w')
    ih.setLevel(logging.INFO)

    eh = logging.FileHandler(os.path.join(BASE_DIR, 'rl5.err'), 'a')
    eh.setLevel(logging.WARNING)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    ih.setFormatter(formatter)
    eh.setFormatter(formatter)

    logger.addHandler(ih)
    logger.addHandler(eh)

    return logger, [ih.stream.fileno(), eh.stream.fileno()]

def run(daemon=False, *args, **kwargs):
    rl5 = RadioLogger()
    rl5.IS_DAEMON = daemon
    rl5.BASE_DIR = BASE_DIR
    rl5.run()

def daemon_run(*args, **kwargs):
    run(True, *args, **kwargs)

def will_run_as_daemon():
    return True if len(argv) > 1 and argv[1] == 'daemon' else False

if __name__ == '__main__':
    logger, fds = init_logger()

    try:
        logger.warning('------ Radio Logger 0x{:x} started ------'.format(get_ident()))
        if not will_run_as_daemon():
            run()
        else:
            print('Now running in daemon mode.')

            PID_PATH = os.path.join(BASE_DIR, 'rl5.pid')

            daemon = Daemonize(
                app='rl5', 
                pid=PID_PATH, 
                action=daemon_run, 
                logger=logger,
                keep_fds=fds,
                chdir=BASE_DIR,
            )
            daemon.start()

    except Exception as e:
        logger.exception('Fatal exception occured: {}'.format(e))
        raise
    finally:
        logger.warning('------ Radio Logger 0x{:x} exited ------'.format(get_ident()))
