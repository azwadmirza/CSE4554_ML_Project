    def _join_index_objects(axis, indexes, how, sort):
        """
        Join the pair of index objects (columns or rows) by a given strategy.

        Unlike Index.join() in Pandas, if axis is 1, the sort is
        False, and how is "outer", the result will _not_ be sorted.

        Parameters
        ----------
        axis : 0 or 1
            The axis index object to join (0 - rows, 1 - columns).
        indexes : list(Index)
            The indexes to join on.
        how : {'left', 'right', 'inner', 'outer'}
            The type of join to join to make.
        sort : boolean
            Whether or not to sort the joined index

        Returns
        -------
        (Index, func)
            Joined index with make_reindexer func
        """
        assert isinstance(indexes, list)

        # define helper functions
        def merge(left_index, right_index):
            if axis == 1 and how == "outer" and not sort:
                return left_index.union(right_index, sort=False)
            else:
                return left_index.join(right_index, how=how, sort=sort)

        # define condition for joining indexes
        do_join_index = False
        for index in indexes[1:]:
            if not indexes[0].equals(index):
                do_join_index = True
                break

        # define condition for joining indexes with getting indexers
        is_duplicates = any(not index.is_unique for index in indexes) and axis == 0
        indexers = []
        if is_duplicates:
            indexers = [None] * len(indexes)

        # perform joining indexes
        if do_join_index:
            if len(indexes) == 2 and is_duplicates:
                # in case of count of indexes > 2 we should perform joining all indexes
                # after that get indexers
                # in the fast path we can obtain joined_index and indexers in one call
                joined_index, indexers[0], indexers[1] = indexes[0].join(
                    indexes[1], how=how, sort=sort, return_indexers=True
                )
            else:
                joined_index = indexes[0]
                # TODO: revisit for performance
                for index in indexes[1:]:
                    joined_index = merge(joined_index, index)

                if is_duplicates:
                    for i, index in enumerate(indexes):
                        indexers[i] = index.get_indexer_for(joined_index)
        else:
            joined_index = indexes[0].copy()

        def make_reindexer(do_reindex: bool, frame_idx: int):
            # the order of the frames must match the order of the indexes
            if not do_reindex:
                return lambda df: df

            if is_duplicates:
                assert indexers != []

                return lambda df: df._reindex_with_indexers(
                    {0: [joined_index, indexers[frame_idx]]},
                    copy=True,
                    allow_dups=True,
                )

            return lambda df: df.reindex(joined_index, axis=axis)

        return joined_index, make_reindexer