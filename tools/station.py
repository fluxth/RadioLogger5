from tools import Tool
from tools.utils.searchers import SpotifySearcher

from common.models import Station, Track

import colorama

class StationTool(Tool):
    
    def list(self):
        with self.db.session_scope() as sess:
            stations = sess.query(Station).all()
            print('Stations [{}]:'.format(len(stations)))

            for station in stations:
                print('- [id={}] {}'.format(station.id, station.name))

    def link_spotify(self, station_name):
        with self.db.session_scope() as sess:
            station = sess.query(Station).filter_by(name=station_name).first()

            if station is None:
                print('Linking failed, station "{}" not found.'.format(station_name))
                return False

            tracks = sess.query(Track)\
                .filter_by(station=station)\
                .filter_by(is_default=False)\
                .all()
                #.limit(10)\

            total_tracks = len(tracks)

            print('Linking {} tracks in station {} to Spotify...'.format(total_tracks, station.name))

            searcher = SpotifySearcher(self.config.get('spotify_searcher'))

            cnt = 1
            for track in tracks:

                uri = track.get_extra('spuri', raise_error=False)
                if uri is not None and 'spotify:' in uri:
                    print(colorama.Fore.YELLOW + '\n\n[{}/{}] Skipping "{}" by "{}", Spotify URI already detected.'.format(
                        cnt,
                        total_tracks,
                        track.title,
                        track.artist
                    ) + colorama.Style.RESET_ALL)
                else:
                    print(colorama.Fore.CYAN + '\n\n[{}/{}] Processing "{}" by "{}"...'.format(
                        cnt,
                        total_tracks,
                        track.title,
                        track.artist
                    ) + colorama.Style.RESET_ALL)

                    result = searcher.search(track.title, track.artist)

                    if result is False:
                        choice = input(colorama.Fore.RED + 'Track not found, manually insert URI? [y/N] > ' + colorama.Style.RESET_ALL).lower()

                        if choice == 'y':
                            while True:
                                uri = input('Spotify URI > ')

                                if 'spotify:track:' in uri:
                                    result = uri
                                    break

                                elif uri == 'c':
                                    print(colorama.Fore.RED + 'Spotify not linked for this track.' + colorama.Style.RESET_ALL)
                                    continue

                                else:
                                    print(colorama.Fore.YELLOW + 'Unrecognized URI, example URI: "spotify:track:58xnXpPVENyQQtgvKh16Fs"'  + colorama.Style.RESET_ALL)

                        else:
                            print(colorama.Fore.RED + 'Spotify not linked for this track.' + colorama.Style.RESET_ALL)
                            continue
                            
                    track.set_extra('spuri', result)
                    sess.add(track)

                    sess.commit()

                cnt += 1
