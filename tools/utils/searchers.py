import requests
import urllib.parse
import re
import colorama

class SpotifySearcher():
    BASE_URL = 'https://api.spotify.com/v1/search'
    VALID_TYPES = ['album', 'artist', 'playlist', 'track']

    def __init__(self, config):
        if config['token'] is None or len(config['token']) <= 0:
            raise SpotifySearcherException('"token" config parameter is required.')
        else:
            self.TOKEN = config['token']

    def build_query(self, title, artist, level):

        # High Confidence

        if level == 0:
            return '{} {}'.format(title, artist)

        elif level == 1:
            if '(' not in title:
                return None

            title = title.split('(')[0].strip()
            return '{} {}'.format(title, artist)

        elif level == 2:
            if 'ft.' not in title.lower():
                return None

            title = title.lower().split('ft.')[0].strip()
            return '{} {}'.format(title, artist)

        elif level == 3:
            if 'feat.' not in title.lower():
                return None

            title = title.lower().split('feat.')[0].strip()
            return '{} {}'.format(title, artist)

        # Medium Confidence

        elif level == 4:
            if '(' not in artist:
                return None

            artist = artist.split('(')[0].strip()
            return '{} {}'.format(title, artist)

        elif level == 5:
            if '(' not in title or '(' not in artist:
                return None

            title = title.split('(')[0].strip()
            artist = artist.split('(')[0].strip()
            return '{} {}'.format(title, artist)

        # Low Confidence

        elif level == 6:
            return title

        elif level == 7:
            if '(' not in title:
                    return None

            return title.split('(')[0].strip()

        elif level == 8:
            if 'ft.' not in title.lower():
                return None

            return title.lower().split('ft.')[0].strip()

        elif level == 9:
            if 'feat.' not in title.lower():
                return None

            return title.lower().split('feat.')[0].strip()

        else:
            return False

    def parse_metadata(self, track):
        # Output: otitle, oartist, oalbum
        return track['name'], ', '.join(a['name'] for a in track['artists']), track['album']['name']

    def format_track(self, title, artist, album):
        return f'{colorama.Fore.MAGENTA}"{title}"{colorama.Style.RESET_ALL} ' + \
        f'by {colorama.Fore.MAGENTA}"{artist}"{colorama.Style.RESET_ALL} in album "{album}"'

    def print_match(self, title, artist, album, level=None):
        out = f'{colorama.Fore.GREEN}Matched{colorama.Style.RESET_ALL} ' + self.format_track(title, artist, album)

        if level is not None:
            out += f' {colorama.Fore.YELLOW}[L{level}]{colorama.Style.RESET_ALL}'

        print(out)

    def link(self, uri):
        track_id = uri.replace('spotify:track:', '')

        resp = requests.get(
            'https://api.spotify.com/v1/tracks/{}'.format(track_id),
            headers = {
                'Authorization': 'Bearer {}'.format(self.TOKEN)
            }
        )

        r = resp.json()

        if not resp.status_code == 200:
            print(colorama.Fore.RED + 'Spotify URI Error {}: {}'.format(r['error']['status'], r['error']['message']) + colorama.Style.RESET_ALL)
            return False

        otitle, oartist, oalbum = self.parse_metadata(r)
        self.print_match(otitle, oartist, oalbum)

        return {
            'uri': r['uri'],
            't': otitle,
            'a': oartist,
        }

    def search(self, title, artist, types=['track']):
        level = 0
        while level <= 9:
            q = self.build_query(title, artist, level)

            if q is None:
                level += 1
                continue

            #print('> lv', level, q)

            data = self.request(q, types)

            if data['tracks']['total'] > 0:
                for r in data['tracks']['items']:
                    otitle, oartist, oalbum = self.parse_metadata(r)

                    if not self.validate_match(title, artist, otitle, oartist):
                        #print('skip')
                        continue

                    self.print_match(otitle, oartist, oalbum, level)
                    #print(colorama.Fore.GREEN + 'Matched "{}" by "{}" in album "{}" [L{}]'.format(otitle, oartist, oalbum, level)  + colorama.Style.RESET_ALL)

                    if level >= 6:
                        choice = input(colorama.Fore.YELLOW + '[LOW CONFIDENCE] Do you want to continue with this match? [y/N/C] > ' + colorama.Style.RESET_ALL).lower()
                        if choice == 'c' or choice == '0':
                            return False
                        elif not (choice == 'y' or choice == '1'):
                            print()
                            continue

                    return {
                        'uri': r['uri'],
                        't': otitle,
                        'a': oartist,
                    }
                else:
                    level += 1
            else:
                level += 1

        else:
            if data is not None and data['tracks']['total'] > 0:
                print(colorama.Fore.RED + 'Auto-detection failed, please manually select a match:' + colorama.Style.RESET_ALL)

                for k, r in enumerate(data['tracks']['items']):
                    otitle, oartist, oalbum = self.parse_metadata(r)
                    print('[{}] {}'.format(k+1, self.format_track(otitle, oartist, oalbum)))

                while True:
                    choice = input(colorama.Fore.YELLOW + 'Selection [{}-{}/C] > '.format(1, len(data['tracks']['items'])) + colorama.Style.RESET_ALL)

                    if choice.lower() == 'c' or choice == '0':
                        return False

                    elif choice.isdigit() and int(choice) > 0 and int(choice) <= len(data['tracks']['items']):
                        r = data['tracks']['items'][int(choice)-1]
                        otitle, oartist, oalbum = self.parse_metadata(r)
           
                        self.print_match(otitle, oartist, oalbum, level)
                        return {
                            'uri': r['uri'],
                            't': otitle,
                            'a': oartist,
                        }
                
                    else:
                        print('Selection out of bound, check your selection or type C to cancel.')
                        continue

            else:
                # print('Not found')
                return False

    def sanitize_string(self, in_str):
        return re.sub(r'[^\w ]+', '', in_str).replace('ๆ', '')

    def validate_match(self, in_title, in_artist, out_title, out_artist):
        if all(w in self.sanitize_string(in_title).split(' ') for w in self.sanitize_string(out_title).split(' ')):
            return True

        return False

    def request(self, query, types):
        if all(t in types for t in self.VALID_TYPES):
            raise SpotifySearcherException('Invalid types: {}'.format(types))

        resp = requests.get(
            '{base}?{q}'.format(
                base = self.BASE_URL,
                q = urllib.parse.urlencode({
                    'q': query,
                    'type': ','.join(types)
                })
            ),
            headers = {
                'Authorization': 'Bearer {}'.format(self.TOKEN)
            }
        )

        data = resp.json()

        if not resp.status_code == 200:
            raise SpotifySearcherException('API Error ({}): "{}"'.format(data['error']['status'], data['error']['message']))

        return data



class SpotifyGoogleSearcher(SpotifySearcher):

    BASE_URL = 'https://www.googleapis.com/customsearch/v1/siterestrict?q={q}&cx={seid}&key={apikey}&exactTerms={exact}track&hl=en'

    def __init__(self, config):
        if config['seid'] is None or len(config['seid']) <= 0:
            raise SpotifySearcherException('"seid" config parameter is required.')
        else:
            self.SEID = config['seid']

        if config['apikey'] is None or len(config['apikey']) <= 0:
            raise SpotifySearcherException('"apikey" config parameter is required.')
        else:
            self.APIKEY = config['apikey']

    def parse_pagetitle(self, pagetitle):
        # [title], a song by [artist] on Spotify
        mid = pagetitle.find(', a song by ')
        end = pagetitle.find(' on Spotify')

        if mid == -1 or end == -1:
            raise Exception('Cannot parse page title "{}"'.format(pagetitle))

        return pagetitle[:mid], pagetitle[mid+12:end]

    def search(self, title, artist, force_track=False):
        level = 0
        while level <= 9:
            q = self.build_query(title, artist, level)

            if q is None:
                level += 1
                continue

            print('lv', level, q)

            data = self.request(q, force_track)
            print(data)
            total = int(data['searchInformation']['totalResults'])

            if total <= 0:
                level += 1
                continue
            else:
                #print(data)

                for result in data['items']:
                    if result['pagemap']['metatags'][0]['og:type']:
                        result_title, result_artist = self.parse_pagetitle(result['pagemap']['metatags'][0]['og:description'])

                        print('"{}" by "{}" -> [{}]'.format(result_title, result_artist, result['link']))
                        return
                    else:
                        print('[{}, {}]'.format(result['title'], result['link']))

    def request(self, q, force_track):
        try:
            resp = requests.get(self.BASE_URL.format(
                q = urllib.parse.quote_plus(q),
                seid = self.SEID,
                apikey = self.APIKEY,
                exact = 'track' if force_track is True else ''
            ))

            return resp.json()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            return False

class SpotifySearcherException(Exception):
    pass