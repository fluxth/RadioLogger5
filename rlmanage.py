import sys
from importlib import import_module

from common.utils import Config
from logger.database import Database

def _(*args, **kwargs):
    return print(*args, **kwargs)

def _e(msg, *args, **kwargs):
    return _('ERROR: {}'.format(msg), *args, **kwargs)

_VERSION = '1.0'
_TOOLS = ['station', 'track']

def print_help():
    # Display USAGE
    _('USAGE: rlmanage.py <tool> [arg0] [arg1] [argn]')
    _('For list of tools, use "rlmanage.py list".')

if __name__ == '__main__':
    _('RLManage v{} for Radio Logger 5\n'.format(_VERSION))

    try:
        config = Config('./config.json')
        db = Database(config.get('database'))
        db.initialize()

        options = sys.argv[1:]

        start = False
        while not start:
            start = True

            if len(options) < 1 or (len(options) == 1 and options[0] == 'help'):
                print_help()
                break

            elif options[0] == 'list':
                if len(_TOOLS) > 0:
                    _('List of avaliable tools:')
                    for tool in _TOOLS:
                        _('- {}'.format(tool))
                else:
                    _('No tools avaliable.')

                break

            elif options[0] in _TOOLS:
                tool = options[0]

                try:
                    t_module = import_module('tools.{}'.format(tool))
                    t_class = getattr(t_module, '{}Tool'.format(tool.title()))

                    t_object = t_class(config, db)

                except (ModuleNotFoundError, AttributeError):
                    _e('Tool error: {}.{} <- {}'.format(tool, method, pass_args))
                    break

                method = options[1].replace('-', '_') if len(options) > 1 else '_default'
                run = getattr(t_object, method)

                pass_args = [] if len(options) < 3 else options[2:]

                try:
                    run(*pass_args)
                except TypeError:
                    _e('Invalid tool usage: {}.{} <- {}'.format(tool, method, pass_args))
                    raise
                    break

            else:
                _e('Tool not found: "{}"\n'.format(options[0]))
                print_help()

                break
    except KeyboardInterrupt:
        _('User exit.')