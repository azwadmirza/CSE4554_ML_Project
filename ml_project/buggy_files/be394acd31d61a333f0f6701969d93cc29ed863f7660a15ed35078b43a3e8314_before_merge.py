    def search(self, query, source=True, context=True, translation=True, checksums=False):
        '''
        Performs full text search on defined set of fields.

        Returns queryset unless checksums is set.
        '''
        ret = set()
        if source or context:
            with FULLTEXT_INDEX.source_searcher(not settings.OFFLOAD_INDEXING) as searcher:
                if source:
                    results = self.__search(
                        searcher,
                        'source',
                        SOURCE_SCHEMA,
                        query
                    )
                    ret = ret.union(results)
                if context:
                    results = self.__search(
                        searcher,
                        'context',
                        SOURCE_SCHEMA,
                        query
                    )
                    ret = ret.union(results)

        if translation:
            sample = self.all()[0]
            with FULLTEXT_INDEX.target_searcher(sample.translation.language.code, not settings.OFFLOAD_INDEXING) as searcher:
                results = self.__search(
                    searcher,
                    'target',
                    TARGET_SCHEMA,
                    query
                )
                ret = ret.union(results)

        if checksums:
            return ret

        return self.filter(checksum__in=ret)