import json
from os.path import join

from server import FRONTEND_DIR


class Errors(object):
    _errors = {}
    _GuestAllowedErrors = (
        (10,None,None),
        (11,None,None),
        (12,None,None),
    )

    def __init__(self):
        with open(join(FRONTEND_DIR, 'src/errors.json'), 'r') as f:
            self._errors = json.load(f)

    def getFromCode(self, code, format_vars={}, **kwargs):
        code = str(code)

        if code == '0':
            return {
                'code': 0,
                'type': 'Unknown Error',
                'name': 'Unknown Error',
                'details': 'Unknown Error'
                **kwargs
            }

        if len(code) == 4:
            root = self._errors[code[0:2]]
            sub = root['children'][code[2]]
            target = sub['children'][code[3]]

            target.update({
                'code': int(code),
                'type': sub['type'],
                **kwargs
            })

            if 'variables' in target:
                # TODO: Check in target.variables to match format_vars
                del target['variables']
                if not format_vars == {}:
                    target.update({
                        'details': target['details'].format(**format_vars)
                    }) 

            return target

        return False

    def getErrors(self):
        return self._errors
