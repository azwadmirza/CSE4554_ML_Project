    def similar(self, unit):
        '''
        Finds similar units to current unit.
        '''
        ret = set([unit.checksum])
        with FULLTEXT_INDEX.source_searcher(not appsettings.OFFLOAD_INDEXING) as searcher:
            # Extract up to 10 terms from the source
            terms = [kw for kw, score in searcher.key_terms_from_text('source', unit.source, numterms=10) if not kw in IGNORE_SIMILAR]
            cnt = len(terms)
            # Try to find at least configured number of similar strings, remove up to 4 words
            while len(ret) < appsettings.SIMILAR_MESSAGES and cnt > 0 and len(terms) - cnt < 4:
                for search in itertools.combinations(terms, cnt):
                    results = self.search(
                        ' '.join(search),
                        True,
                        False,
                        False,
                        True
                    )
                    ret = ret.union(results)
                cnt -= 1

        return self.filter(
            translation__subproject__project=unit.translation.subproject.project,
            translation__language=unit.translation.language,
            checksum__in=ret
        ).exclude(
            target__in=['', unit.target]
        )