    def get_lyrics(self, artist, title):
        """Fetch lyrics, trying each source in turn. Return a string or
        None if no lyrics were found.
        """
        for backend in self.backends:
            lyrics = backend(artist, title)
            if lyrics:
                log.debug(u'got lyrics from backend: {0}'
                          .format(backend.__name__))
                return lyrics.strip()