from flask import request
from authlib.jose import jwt
from datetime import datetime
import base64

from server.error import Errors

JWT_KEY = 'superdooperSEcRet!!'
JWT_HEADER = {
    'alg': 'HS256',
    'typ': 'JWT'
}

def issue_token(username):
    time_now = int(datetime.utcnow().timestamp())
    expires = time_now + 60*60*24

    payload = {
        'sub': username,
        'iat': time_now,
        'exp': expires,
    }

    return {
        'username': username,
        'accessToken': base64.b64encode(jwt.encode(JWT_HEADER, payload, JWT_KEY)).decode('utf-8'),
        'expires': expires
    }

def validate_token(token, error_handler):
    claims = jwt.decode(base64.b64decode(token), JWT_KEY)

    if claims.get('sub') == 'flux':
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
        return error_handler.getFromCode(1201)

    if not validate_token(token, error_handler):
        # Error: Invalid token
        return error_handler.getFromCode(1202)

    return True