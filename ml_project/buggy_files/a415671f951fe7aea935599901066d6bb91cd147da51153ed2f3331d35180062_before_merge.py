    def parse_movie(self, data, **kwargs):
        log.debug('Parsing movie: `%s` [options: %s]', data, kwargs)
        start = time.clock()
        guessit_options = self._guessit_options(kwargs)
        guessit_options['type'] = 'movie'
        guess_result = guessit_api.guessit(data, options=guessit_options)
        # NOTE: Guessit expects str on PY3 and unicode on PY2 hence the use of future.utils.native
        parsed = GuessitParsedMovie(native(data), kwargs.pop('name', None), guess_result, **kwargs)
        end = time.clock()
        log.debug('Parsing result: %s (in %s ms)', parsed, (end - start) * 1000)
        return parsed