    def remove(self, indexer, indexer_id):
        """Remove cache item given indexer and indexer_id."""
        with self.lock:
            to_remove = [
                cached_name
                for cached_name, cached_parsed_result in iteritems(self.cache)
                if cached_parsed_result.series.indexer == indexer
                and cached_parsed_result.series.indexerid == indexer_id
            ]
            for item in to_remove:
                del self.cache[item]
                log.debug('Removed cached parse result for {name}', {'name': item})