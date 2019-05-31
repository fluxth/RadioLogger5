from tools import Tool


class ConfigTool(Tool):
    def spotify_token(self, mode, value=None):
        if mode == 'get':
            print(self.config.get('spotify_searcher.token'))
        elif mode == 'set':
            if value is None:
                print('Please provide the token to set.')
                return False

            self.config.set('spotify_searcher.token', value)
            print('New token set.')
        else:
            print(f'Unknown mode: {mode}')