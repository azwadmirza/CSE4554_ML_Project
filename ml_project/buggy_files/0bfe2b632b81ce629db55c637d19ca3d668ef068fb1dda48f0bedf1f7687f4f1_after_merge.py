    def authenticate(self, c_key, c_secret):
        # Get the link for the OAuth page.
        auth_client = Client(USER_AGENT, c_key, c_secret)
        try:
            _, _, url = auth_client.get_authorize_url()
        except CONNECTION_ERRORS as e:
            self._log.debug('connection error: {0}', e)
            raise beets.ui.UserError('communication with Discogs failed')

        beets.ui.print_("To authenticate with Discogs, visit:")
        beets.ui.print_(url)

        # Ask for the code and validate it.
        code = beets.ui.input_("Enter the code:")
        try:
            token, secret = auth_client.get_access_token(code)
        except DiscogsAPIError:
            raise beets.ui.UserError('Discogs authorization failed')
        except CONNECTION_ERRORS as e:
            self._log.debug(u'connection error: {0}', e)
            raise beets.ui.UserError('Discogs token request failed')

        # Save the token for later use.
        self._log.debug('Discogs token {0}, secret {1}', token, secret)
        with open(self._tokenfile(), 'w') as f:
            json.dump({'token': token, 'secret': secret}, f)

        return token, secret