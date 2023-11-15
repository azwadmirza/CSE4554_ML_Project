    def parse_series(self, data, **kwargs):
        log.debug('Parsing series: `%s` kwargs: %s', data, kwargs)
        start = time.clock()
        parser = SeriesParser(**kwargs)
        try:
            parser.parse(data)
        except ParseWarning as pw:
            log_once(pw.value, logger=log)
        # TODO: Returning this invalid object seems a bit silly, raise an exception is probably better
        if not parser.valid:
            return SeriesParseResult(valid=False)
        result = SeriesParseResult(
            data=data,
            name=parser.name,
            episodes=parser.episodes,
            id=parser.id,
            id_type=parser.id_type,
            quality=parser.quality,
            proper_count=parser.proper_count,
            special=parser.special,
            group=parser.group,
            season_pack=parser.season_pack,
            strict_name=parser.strict_name,
            identified_by=parser.identified_by
        )
        end = time.clock()
        log.debug('Parsing result: %s (in %s ms)', parser, (end - start) * 1000)
        return result