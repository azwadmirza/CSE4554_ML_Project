    def parse_series(self, data, **kwargs):
        log.debug('Parsing series: `%s` kwargs: %s', data, kwargs)
        start = time.clock()
        parser = SeriesParser(**kwargs)
        try:
            parser.parse(data)
        except ParseWarning as pw:
            log_once(pw.value, logger=log)
        end = time.clock()
        log.debug('Parsing result: %s (in %s ms)', parser, (end - start) * 1000)
        return parser