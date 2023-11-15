    def remove(self, indexer, indexer_id):
        """Remove cache item given indexer and indexer_id."""
        if not indexer or not indexer_id:
            return
        to_remove = [
            cached_name
            for cached_name, cached_parsed_result in iteritems(self.cache)
            if cached_parsed_result.series.indexer == indexer
            and cached_parsed_result.series.indexerid == indexer_id
        ]
        for item in to_remove:
            del self.cache[item]
            log.debug('Removed parsed cached result for release: {release}'.format(release=item))