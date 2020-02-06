from flask import send_from_directory

import os.path

from server.auth import check_auth
from server.api import (
    handle_api,
    api_authenticate,
)

from . import BUILD_DIR


def serve_api(path):
    # /authenticate $
    if path == 'authenticate':
        return api_authenticate()

    auth = check_auth()
    if not auth is True:
        return auth

    # /*
    return handle_api(path)

def serve_react(path):
    if path == '':
        path = 'index.html'
    elif not os.path.isfile(os.path.join(BUILD_DIR, path)):
        path = 'index.html'

    return send_from_directory(BUILD_DIR, path)