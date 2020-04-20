from flask import send_from_directory

import os.path

from server.auth import check_auth
from server.api import (
    handle_guest_api,
    handle_authenticated_api,
    api_authenticate,
    get_error_json
)

from . import BUILD_DIR


def serve_api(path):
    GUEST_ENDPOINTS = ['authenticate']
    if path in GUEST_ENDPOINTS:
        return handle_guest_api(path)

    auth = check_auth()
    if auth is not True:
        return get_error_json(auth)

    return handle_authenticated_api(path)

def serve_react(path):
    if path == '':
        path = 'index.html'
    elif not os.path.isfile(os.path.join(BUILD_DIR, path)):
        path = 'index.html'

    return send_from_directory(BUILD_DIR, path)