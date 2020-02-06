from flask import send_file, send_from_directory, request
from flask.json import jsonify
import os.path
from datetime import datetime, timezone

from common.models import Station, Play

from . import BUILD_DIR

from time import sleep

def validate_token(token):
    if token == 'asdf':
        return True

    return False

def check_auth():
    token = request.headers.get('Authorization', None)
    if token is None:
        token = request.args.get('access_token', None)
    else:
        token = token.replace('Bearer ', '')

    if token is None:
        return jsonify({
            'status': 'error',
            'error': {
                'code': 1201,
                'type': 'Authentication Error',
                'message': 'A token is required to access this resource'
            }
        })

    if not validate_token(token):
        return jsonify({
            'status': 'error',
            'error': {
                'code': 1202,
                'type': 'Authentication Error',
                'message': 'Invalid token'
            }
        })

    return True

def serve_api(path):
    
    if path == 'authenticate':
        return jsonify({
            'status': 'ok',
            'data': {
                'username': 'lolz',
                'accessToken': 'asdf',
                'expires': int(datetime.utcnow().timestamp()) + 60*60*24,
            },
            '_ts': int(datetime.utcnow().timestamp())
        })

    auth = check_auth()
    if not auth is True:
        return auth

    data = None
    error = None
    payload_add = {}

    segment = path.split('/')

    if path == 'stations':
        stations = Station.query.all()
        data = []

        for s in stations:
            last_play = Play.query.filter(Play.track.has(station=s))\
                            .order_by(Play.id.desc())\
                            .first().ts

            station_data = {
                'id': s.id,
                'name': s.name,
                'tracks': len(s.tracks),
                'last_play': last_play.replace(tzinfo=timezone.utc).isoformat(),
                'added': s.ts.replace(tzinfo=timezone.utc).isoformat(),
            }


            lp_diff = (datetime.utcnow() - last_play).total_seconds()

            if lp_diff > 0 and lp_diff <= 1500:
                station_data['status'] = 'active'
            else:
                station_data['status'] = 'stalled'
            # TODO: Add disabled status from config too

            data.append(station_data)

    elif path == 'status':
        data = {
            'version': '5.0.1'
        }

    elif segment[0] == 'station' and not int(segment[1]) == 0:

        station_id = int(segment[1])
        station = Station.query.filter_by(id=station_id).first()

        if station is None:
            error = {
                'code': 1301,
                'type': 'Object Not Found',
                'message': 'Station with id="{}" not found'.format(station_id)
            }
        else:
            if segment[2] == 'history':

                limit = int(request.args.get('c', 100))
                modifier = request.args.get('mod', None)
                play_id = int(request.args.get('id', 0))

                history = Play.query.filter(Play.track.has(station=station))

                if modifier == 'old':
                    history = history.filter(Play.id < play_id)
                    payload_add['action'] = 'append'
                elif modifier == 'new':
                    history = history.filter(Play.id > play_id)
                    payload_add['action'] = 'prepend'
                else:
                    payload_add['action'] = 'clear'

                history = history.order_by(Play.id.desc()).limit(limit).all()

                data = [{
                    'id': p.id,
                    'track_id': p.track.id,
                    'title': p.track.title,
                    'artist': p.track.artist,
                    'default': p.track.is_default,
                    'ts': p.ts.replace(tzinfo=timezone.utc).isoformat(),
                } for p in history]

    if data is None or not error is None:
        payload = {
            'status': 'error',
            'error': {
                'code': 1101,
                'type': 'Request Error',
                'message': 'Unknown endpoint'
            }
        }

        if not error is None:
            payload['error'] = error
    else:
        payload = {
            'status': 'ok',
            'data': data,
            '_ts': int(datetime.utcnow().timestamp())
        }

        if not payload_add == {}:
            payload.update(payload_add)

    return jsonify(payload)

def serve_react(path):
    if path == '':
        path = 'index.html'
    elif not os.path.isfile(os.path.join(BUILD_DIR, path)):
        path = 'index.html'

    return send_from_directory(BUILD_DIR, path)