    def __init__(self):
        super(LyricsPlugin, self).__init__()
        self.import_stages = [self.imported]
        self.config.add({
            'auto': True,
            'bing_client_secret': None,
            'bing_lang_from': [],
            'bing_lang_to': None,
            'google_API_key': None,
            'google_engine_ID': u'009217259823014548361:lndtuqkycfu',
            'genius_api_key':
                "Ryq93pUGm8bM6eUWwD_M3NOFFDAtp2yEE7W"
                "76V-uFL5jks5dNvcGCdarqFjDhP9c",
            'fallback': None,
            'force': False,
            'local': False,
            'sources': self.SOURCES,
        })
        self.config['bing_client_secret'].redact = True
        self.config['google_API_key'].redact = True
        self.config['google_engine_ID'].redact = True
        self.config['genius_api_key'].redact = True

        # State information for the ReST writer.
        # First, the current artist we're writing.
        self.artist = u'Unknown artist'
        # The current album: False means no album yet.
        self.album = False
        # The current rest file content. None means the file is not
        # open yet.
        self.rest = None

        available_sources = list(self.SOURCES)
        sources = plugins.sanitize_choices(
            self.config['sources'].as_str_seq(), available_sources)

        if 'google' in sources:
            if not self.config['google_API_key'].get():
                # We log a *debug* message here because the default
                # configuration includes `google`. This way, the source
                # is silent by default but can be enabled just by
                # setting an API key.
                self._log.debug(u'Disabling google source: '
                                u'no API key configured.')
                sources.remove('google')
            elif not HAS_BEAUTIFUL_SOUP:
                self._log.warning(u'To use the google lyrics source, you must '
                                  u'install the beautifulsoup4 module. See '
                                  u'the documentation for further details.')
                sources.remove('google')

        if 'genius' in sources and not HAS_BEAUTIFUL_SOUP:
            self._log.debug(
                u'The Genius backend requires BeautifulSoup, which is not '
                u'installed, so the source is disabled.'
            )
            sources.remove('google')

        self.config['bing_lang_from'] = [
            x.lower() for x in self.config['bing_lang_from'].as_str_seq()]
        self.bing_auth_token = None

        if not HAS_LANGDETECT and self.config['bing_client_secret'].get():
            self._log.warning(u'To use bing translations, you need to '
                              u'install the langdetect module. See the '
                              u'documentation for further details.')

        self.backends = [self.SOURCE_BACKENDS[source](self.config, self._log)
                         for source in sources]