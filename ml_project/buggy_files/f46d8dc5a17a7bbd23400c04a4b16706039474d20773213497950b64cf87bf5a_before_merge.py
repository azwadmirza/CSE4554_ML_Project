    def set_caps(self, data):
        """Set caps."""
        if not data:
            return

        def _parse_cap(tag):
            elm = data.find(tag)
            return elm.get('supportedparams').split(',') if elm and elm.get('available') == 'yes' else []

        self.cap_tv_search = _parse_cap('tv-search')
        # self.cap_search = _parse_cap('search')
        # self.cap_movie_search = _parse_cap('movie-search')
        # self.cap_audio_search = _parse_cap('audio-search')

        # self.params = any([self.cap_tv_search, self.cap_search, self.cap_movie_search, self.cap_audio_search])
        self.params = any([self.cap_tv_search])