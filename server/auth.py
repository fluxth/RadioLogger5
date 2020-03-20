from flask import request

from server.error import Errors
from server.api import get_error_json

def validate_token(token, error_handler):
    if token == 'asdf':
        return True

    return False

def check_auth():

    error_handler = Errors()

    token = request.headers.get('Authorization', None)
    if token is None:
        token = request.args.get('access_token', None)
    else:
        token = token.replace('Bearer ', '')

    if token is None:
        # Error: token required
        return get_error_json(error_handler.getFromCode(1201))

    if not validate_token(token, error_handler):
        # Error: Invalid token
        return get_error_json(error_handler.getFromCode(1202))

    return True