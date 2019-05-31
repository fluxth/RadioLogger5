import sys
from importlib import import_module

from common.utils import Config
from logger.database import Database

def _(*args, **kwargs):
    return print(*args, **kwargs)

def _e(msg, *args, **kwargs):
    return _(f'ERROR: {msg}', *args, **kwargs)

_VERSION = '1.0'
_TOOLS = ['station', 'track', 'config']
_TOOL_SWAP_ARGS = ['station', 'config']

def print_help():
    # Display USAGE
    _('USAGE: rlmanage.py <tool> [arg0] [arg1] [argn]')
    _('For list of tools, use "rlmanage.py list".')

if __name__ == '__main__':
    _(f'RLManage v{_VERSION} for Radio Logger 5\n')

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
                        _(f'- {tool}')
                else:
                    _('No tools avaliable.')

                break

            elif options[0] in _TOOLS:
                tool = options[0]

                try:
                    t_module = import_module(f'tools.{tool}')
                    t_class = getattr(t_module, f'{tool.title()}Tool')

                    t_object = t_class(config, db)

                except (ModuleNotFoundError, AttributeError):
                    _e(f'Tool error: {tool}.{method} <- {pass_args}')
                    break

                if tool in _TOOL_SWAP_ARGS and len(options) >= 3:
                    # tool arg2 arg1 arg3 ...
                    method = options[2]
                    pass_args = [options[1]] + ([] if len(options) < 3 else options[3:])
                else:
                    # tool arg1 arg2 arg3 ...
                    method = options[1] if len(options) > 1 else '_default'
                    pass_args = [] if len(options) < 3 else options[2:]

                method = method.replace('-', '_')

                run = getattr(t_object, method)

                try:
                    run(*pass_args)
                except TypeError:
                    _e(f'Invalid tool usage: {tool}.{method} <- {pass_args}')
                    raise
                    break

            else:
                _e(f'Tool not found: "{options[0]}"\n')
                print_help()

                break
    except KeyboardInterrupt:
        _('User exit.')