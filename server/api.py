from flask import request
from flask.json import jsonify

from datetime import datetime, timezone

from common.models import Station, Play

from server.error import Errors


def get_data_json(data={}, status='ok', data_count=False, **kwargs):
    payload = {
        'status': status,
        'data': data,
        **kwargs,
        '_ts': int(datetime.utcnow().timestamp())
    }

    if data_count is True and data.__class__ is list:
        payload['data_count'] = len(data)

    return jsonify(payload)

def get_error_json(error={ 'code': 0, 'type': 'Unknown Error', 'message': 'Unknown error occured' }, **kwargs):
    return jsonify({
        'status': 'error',
        'error': error,
        **kwargs,
        '_ts': int(datetime.utcnow().timestamp())
    })


def api_authenticate(error_handler):
    if True:
        return get_data_json({
            'username': 'flux',
            'accessToken': 'asdf',
            'expires': int(datetime.utcnow().timestamp()) + 60*60*24,
        })

    # Error: Invalid credentials
    return get_error_json(error_handler.getFromCode(1212))

def api_status():
    return get_data_json({
        # TODO: Dynamic from daemon
        'version': '5.0-BETA'
    })

def api_stations():
    stations = Station.query.all()
    data = []

    for s in stations:
        last_play = Play.query.filter(Play.track.has(station=s))\
                        .order_by(Play.id.desc())\
                        .first()

        if last_play is not None:
            last_play = last_play.ts

        station_data = {
            'id': s.id,
            'name': s.name,
            'tracks': len(s.tracks),
            'added': s.ts.replace(tzinfo=timezone.utc).isoformat(),
        }

        if last_play is not None:
            station_data['last_play'] = last_play.replace(tzinfo=timezone.utc).isoformat()
            lp_diff = (datetime.utcnow() - last_play).total_seconds()

            if lp_diff > 0 and lp_diff <= 1500:
                station_data['status'] = 'active'
            else:
                station_data['status'] = 'stalled'
            # TODO: Add disabled status from config too
        else:
            station_data['last_play'] = None
            station_data['status'] = 'stalled'

        data.append(station_data)

    return get_data_json(data, data_count=True)

def api_station_history(station):
    limit = int(request.args.get('c', 100))
    modifier = request.args.get('mod', None)
    play_id = int(request.args.get('id', 0))

    if limit > 200:
        limit = 200

    history = Play.query.filter(Play.track.has(station=station))

    payload_add = {}
    if modifier == 'old':
        history = history.filter(Play.id < play_id)
        payload_add['action'] = 'append'
    elif modifier == 'new':
        history = history.filter(Play.id > play_id)
        payload_add['action'] = 'prepend'
    else:
        payload_add['action'] = 'clear'

    history = history.order_by(Play.id.desc()).limit(limit).all()

    return get_data_json([{
        'id': p.id,
        'track_id': p.track.id,
        'title': p.track.title,
        'artist': p.track.artist,
        'default': p.track.is_default,
        'ts': p.ts.replace(tzinfo=timezone.utc).isoformat(),
    } for p in history], data_count=True, **payload_add)

def handle_unknown_endpoint(path, error_handler):
    # Error: Endpoint not found
    return get_error_json(error_handler.getFromCode(1101, format_vars={ 'path': path }))

def handle_guest_api(path):
    # segment = path.split('/')
    error_handler = Errors()

    # /authenticate $
    if path == 'authenticate':
        return api_authenticate(error_handler)

    # Error: Endpoint not found
    return handle_unknown_endpoint(path, error_handler)

def handle_authenticated_api(path):
    segment = path.split('/')
    error_handler = Errors()

    # /status $
    if path == 'status':
        return api_status()

    # /stations $
    if path == 'stations':
        return api_stations()
    
    # /station/{id}
    if segment[0] == 'station' and not int(segment[1]) == 0:

        station_id = int(segment[1])
        station = Station.query.filter_by(id=station_id).first()

        if station is None:
            # Error: Station not found
            return get_error_json(error_handler.getFromCode(1301, message=f'Station with id="{station_id}" not found'))

        else:
            # /station/{id}/history $
            if segment[2] == 'history' and len(segment) == 3:
                return api_station_history(station)
                
    # Error: Endpoint not found
    return handle_unknown_endpoint(path, error_handler)