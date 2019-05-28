from tools import Tool
from tools.utils.searchers import SpotifySearcher

from common.models import Track


class TrackTool(Tool):
    def edit_spotify(self, track_id):
        with self.db.session_scope() as sess:
            track = sess.query(Track).filter_by(id=track_id).first()

            if track is None:
                print('Cannot edit, track ID "{}" not found.'.format(track_id))
                return False

            sp = track.get_extra('sp', raise_error=False)
            if sp is not None and 'uri' in sp and sp['uri'] is not None:
                print(f'Track ({track_id}) "{track.title}" by "{track.artist}" has the following spotify metadata:\n')

                print(f"URI: {sp['uri']}")
                print(f"Title: {sp['t']}")
                print(f"Artist: {sp['a']}")

            else:
                print(f'Track ({track_id}) "{track.title}" by "{track.artist}" has no spotify metadata.')

            choice = input('\nEdit this track\'s metadata? [y/N] > ').lower()
            if choice == 'y':

                searcher = SpotifySearcher(self.config.get('spotify_searcher'))

                while True:
                    uri = input('Enter new Spotify URI [enter "d" to clear/C] > ')

                    if uri.lower() == 'd':
                        self._clear_spotify(track)
                        print(f'Metadata cleared for track ID: {track_id}')
                        return True

                    elif uri.lower() == 'c':
                        print(f'Abort metadata editing.')
                        return False

                    elif 'spotify:track:' in uri:
                        result = searcher.link(uri)

                        if result is False:
                            continue

                        track.set_extra('sp', result)
                        sess.commit()
                        break
                    else:
                        print('Invalid URI detected, please try again.\n')
                        continue


    def _clear_spotify(self, track):
        orig = track.get_extra('.', raise_error=False)

        if orig is not None:
            if 'sp' in orig:
                del orig['sp']

            if 'spuri' in orig:
                del orig['spuri']

            if bool(orig) is False:
                track.extras = None
            else:
                track.set_extra('.', orig)
