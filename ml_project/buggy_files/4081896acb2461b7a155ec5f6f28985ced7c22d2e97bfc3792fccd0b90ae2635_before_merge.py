    def parse_series(self, data, **kwargs):
        log.debug('Parsing series: `%s` [options: %s]', data, kwargs)
        guessit_options = self._guessit_options(kwargs)
        if kwargs.get('name') and not guessit_options.get('strict_name'):
            expected_title = kwargs['name']
            expected_title = expected_title.replace('\'', '(?:\'|\\\'|\\\\\'|-|)?')  # apostrophe support
            guessit_options['expected_title'] = ['re:' + expected_title]
        if kwargs.get('id_regexps'):
            guessit_options['id_regexps'] = kwargs.get('id_regexps')
        start = time.clock()
        # If no series name is provided, we don't tell guessit what kind of match we are looking for
        # This prevents guessit from determining that too general of matches are series
        parse_type = 'episode' if kwargs.get('name') else None
        if parse_type:
            guessit_options['type'] = parse_type

        # NOTE: Guessit expects str on PY3 and unicode on PY2 hence the use of future.utils.native
        try:
            guess_result = guessit_api.guessit(native(data), options=guessit_options)
        except GuessitException:
            log.warning('Parsing %s with guessit failed. Most likely a unicode error.', data)
            guess_result = {}
        parsed = GuessitParsedSerie(data, kwargs.pop('name', None), guess_result, **kwargs)
        end = time.clock()
        log.debug('Parsing result: %s (in %s ms)', parsed, (end - start) * 1000)
        return parsed