    def add_cache_entry(self, name, url, seeders, leechers, size, pubdate, parsed_result=None):
        """Add item into cache database."""
        try:
            # Use the already passed parsed_result of possible.
            parse_result = parsed_result or NameParser().parse(name)
        except (InvalidNameException, InvalidShowException) as error:
            log.debug('{0}', error)
            return None

        if not parse_result or not parse_result.series_name:
            return None

        # add the parsed result to cache for usage later on
        season = 1
        if parse_result.season_number is not None:
            season = parse_result.season_number

        episodes = parse_result.episode_numbers

        if season is not None and episodes is not None:
            # store episodes as a separated string
            episode_text = '|{0}|'.format(
                '|'.join({str(episode) for episode in episodes if episode})
            )

            # get the current timestamp
            cur_timestamp = int(time())

            # get quality of release
            quality = parse_result.quality

            assert isinstance(name, text_type)

            # get release group
            release_group = parse_result.release_group

            # get version
            version = parse_result.version

            # Store proper_tags as proper1|proper2|proper3
            proper_tags = '|'.join(parse_result.proper_tags)

            if not self.item_in_cache(url):
                log.debug('Added item: {0} to cache: {1} with url {2}', name, self.provider_id, url)
                return [
                    'INSERT INTO [{name}] '
                    '   (name, season, episodes, indexerid, url, time, quality, '
                    '    release_group, version, seeders, leechers, size, pubdate, '
                    '    proper_tags, date_added, indexer ) '
                    'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'.format(
                        name=self.provider_id
                    ),
                    [name, season, episode_text, parse_result.series.series_id, url,
                     cur_timestamp, quality, release_group, version,
                     seeders, leechers, size, pubdate, proper_tags, cur_timestamp, parse_result.series.indexer]
                ]
            else:
                log.debug('Updating item: {0} to cache: {1}', name, self.provider_id)
                return [
                    'UPDATE [{name}] '
                    'SET name=?, season=?, episodes=?, indexer=?, indexerid=?, '
                    '    time=?, quality=?, release_group=?, version=?, '
                    '    seeders=?, leechers=?, size=?, pubdate=?, proper_tags=? '
                    'WHERE url=?'.format(
                        name=self.provider_id
                    ),
                    [name, season, episode_text, parse_result.series.indexer, parse_result.series.series_id,
                     cur_timestamp, quality, release_group, version,
                     seeders, leechers, size, pubdate, proper_tags, url]
                ]