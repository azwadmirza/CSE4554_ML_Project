    def ref_locs(self):
        if self._ref_locs is None:
            indexer = self.ref_items.get_indexer(self.items)
            indexer = com._ensure_platform_int(indexer)
            assert((indexer != -1).all())
            self._ref_locs = indexer
        return self._ref_locs