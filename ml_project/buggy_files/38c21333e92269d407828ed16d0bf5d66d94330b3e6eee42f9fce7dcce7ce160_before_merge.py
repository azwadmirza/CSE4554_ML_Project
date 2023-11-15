    def parse_movie(self, data, **kwargs):
        log.debug('Parsing movie: `%s` kwargs: %s', data, kwargs)
        start = time.clock()
        parser = MovieParser()
        try:
            parser.parse(data)
        except ParseWarning as pw:
            log_once(pw.value, logger=log)
        end = time.clock()
        log.debug('Parsing result: %s (in %s ms)', parser, (end - start) * 1000)
        return parser