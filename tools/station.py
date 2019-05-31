from tools import Tool
from tools.track import TrackTool
from tools.utils.searchers import SpotifySearcher

from common.models import Station, Track, Play
from sqlalchemy import func, desc

import requests
import colorama
import math

class StationTool(Tool):
    
    def list(self):
        with self.db.session_scope() as sess:
            stations = sess.query(Station).all()
            print('Stations [{}]:'.format(len(stations)))

            for station in stations:
                print('- [id={}] {}'.format(station.id, station.name))

    def search_title(self, station_name, query):
        with self.db.session_scope() as sess:
            station = sess.query(Station).filter_by(name=station_name).first()

            if station is None:
                print('Search failed, station "{}" not found.'.format(station_name))
                return False

            tracks = sess.query(Track)\
                .filter_by(station=station)\
                .filter_by(is_default=False)\
                .filter(Track.title.like(f'%{query}%'))\
                .all()

            for track in tracks:
                print(f'[ID={track.id}] "{track.title}" by "{track.artist}"')
        

    def clear_spotify(self, station_name, track_ids=None):
        with self.db.session_scope() as sess:
            station = sess.query(Station).filter_by(name=station_name).first()

            if station is None:
                print('Clearing failed, station "{}" not found.'.format(station_name))
                return False

            print('Warning: This will erase ALL spotify metadata from this station!')
            if not input('If you wish to continue, please type station name ({}) to confirm > '.format(station.name)).lower() == station.name.lower():
                print('Clearing aborted.')
                return False

            tracks = sess.query(Track)\
                .filter_by(station=station)\
                .filter_by(is_default=False)\
                .all()

            print('Clearing Spotify metadata for {} tracks in station {}...'.format(len(tracks), station.name))

            tool = TrackTool(self.config, self.db)
            for track in tracks:
                tool._clear_spotify(track)
                sess.commit()
                #print(track.extras)

            print('Success!')

    def gen_spotify(self, station_name):
        with self.db.session_scope() as sess:
            station = sess.query(Station).filter_by(name=station_name).first()

            if station is None:
                print('Playlist generation failed, station "{}" not found.'.format(station_name))
                return False

            q = sess.query(Track, func.count(Track.plays).label('spins'))\
                .join(Play)\
                .filter(Play.track.has(Track.station_id == station.id))\
                .filter(Play.track.has(Track.is_default == False))\
                .group_by(Track)\
                .order_by(desc('spins'))
            tracks = q.all()

            print(f'Generating Spotify playlist for {len(tracks)} tracks...')

            out = []
            skipped = 0
            dupes = 0
            for track in tracks:
                uri = track[0].get_extra('sp.uri', raise_error=False)

                if uri is not None:
                    if uri in out:
                        dupes += 1
                    else:
                        out.append(uri)
                else:
                    skipped += 1

            print(f'Processed {len(tracks)} total tracks, {skipped} skipped, {dupes} duplicates.\n')
            if not input('Inject to Spotify? [y/N] > ').lower() == 'y':
                print('\n' + ','.join(out))
                return True
            else:
                playlist_id = input('\nPLAYLIST ID > ')
                token = input('TOKEN > ')
                print()

                URL = 'https://api.spotify.com/v1/playlists/{}/tracks?uris={}'

                loops = math.ceil(len(out) / 100)

                c = 0
                while c < loops:
                    payload = out[(c*100):(c*100)+100]

                    resp = requests.post(
                        URL.format(playlist_id, ','.join(payload)),
                        headers = {
                            'Authorization': f'Bearer {token}'
                        }
                    )

                    data = resp.json()

                    if 'error' in data:
                        print('Spotify API Error {}: {}'.format(data['error']['status'], data['error']['message']))
                        return False

                    if 'snapshot_id' in data:
                        print(f'{len(payload)} tracks added, snapshot "{data["snapshot_id"]}"')

                    c += 1


    def link_spotify(self, station_name, order='plays'):
        with self.db.session_scope() as sess:
            station = sess.query(Station).filter_by(name=station_name).first()

            if station is None:
                print('Linking failed, station "{}" not found.'.format(station_name))
                return False

            if order == 'start':
                tracks = sess.query(Track)\
                    .filter_by(station=station)\
                    .filter_by(is_default=False)\
                    .order_by(Track.id)\
                    .all()
            elif order == 'end':
                tracks = sess.query(Track)\
                    .filter_by(station=station)\
                    .filter_by(is_default=False)\
                    .order_by(desc(Track.id))\
                    .all()
            elif order == 'plays':
                tracks = sess.query(Track, func.count(Track.plays).label('spins'))\
                    .join(Play)\
                    .filter(Play.track.has(Track.station_id == station.id))\
                    .filter(Play.track.has(Track.is_default == False))\
                    .group_by(Track)\
                    .order_by(desc('spins'))\
                    .all()

                tracks = [tr[0] for tr in tracks]
            else:
                print(f'Unknown order: {order}')
                return False

            total_tracks = len(tracks)

            print('Linking {} tracks in station {} to Spotify...'.format(total_tracks, station.name))

            searcher = SpotifySearcher(self.config.get('spotify_searcher'))

            cnt = 0
            for track in tracks:
                cnt += 1
                uri = track.get_extra('sp.uri', raise_error=False)
                if uri is not None and 'spotify:' in uri:
                    continue
                    print(colorama.Fore.YELLOW + '\n\n[{}/{}] Skipping "{}" by "{}", Spotify URI already detected.'.format(
                        cnt,
                        total_tracks,
                        track.title,
                        track.artist
                    ) + colorama.Style.RESET_ALL)
                else:
                    print('\n\n{c}[{}/{}] Processing [{}] {r}{m}"{}"{r}{c} by {r}{m}"{}"{r}{c}...{r}'.format(
                        cnt,
                        total_tracks,
                        track.id,
                        track.title,
                        track.artist,
                        m=colorama.Fore.MAGENTA,
                        c=colorama.Fore.CYAN,
                        r=colorama.Style.RESET_ALL,
                    ))

                    result = searcher.search(track.title, track.artist)

                    if result is False:
                        choice = input(colorama.Fore.RED + 'Track not found, manually insert URI? [y/N] > ' + colorama.Style.RESET_ALL).lower()

                        if choice == 'y' or choice == '1':
                            while True:
                                uri = input('Spotify URI > ')

                                if 'spotify:track:' in uri:
                                    result = searcher.link(uri)

                                    if result is False:
                                        continue

                                    break

                                elif uri == 'c':
                                    print(colorama.Fore.RED + 'Spotify not linked for this track.' + colorama.Style.RESET_ALL)
                                    continue

                                else:
                                    print(colorama.Fore.YELLOW + 'Unrecognized URI, example URI: "spotify:track:58xnXpPVENyQQtgvKh16Fs"'  + colorama.Style.RESET_ALL)

                        else:
                            print(colorama.Fore.RED + 'Spotify not linked for this track.' + colorama.Style.RESET_ALL)
                            continue
                            
                    track.set_extra('sp', result)
                    sess.add(track)

                    sess.commit()
                    #print(track.extras)
                    