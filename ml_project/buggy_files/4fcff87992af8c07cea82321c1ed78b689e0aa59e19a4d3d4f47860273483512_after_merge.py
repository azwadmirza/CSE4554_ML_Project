    def _interleave(self, items):
        """
        Return ndarray from blocks with specified item order
        Items must be contained in the blocks
        """
        dtype = _interleaved_dtype(self.blocks)
        items = _ensure_index(items)

        result = np.empty(self.shape, dtype=dtype)
        itemmask = np.zeros(len(items), dtype=bool)

        # By construction, all of the item should be covered by one of the
        # blocks
        if items.is_unique:
            for block in self.blocks:
                indexer = items.get_indexer(block.items)
                assert((indexer != -1).all())
                result[indexer] = block.get_values(dtype)
                itemmask[indexer] = 1
        else:
            for block in self.blocks:
                mask = items.isin(block.items)
                indexer = mask.nonzero()[0]
                assert(len(indexer) == len(block.items))
                result[indexer] = block.get_values(dtype)
                itemmask[indexer] = 1

        assert(itemmask.all())

        return result