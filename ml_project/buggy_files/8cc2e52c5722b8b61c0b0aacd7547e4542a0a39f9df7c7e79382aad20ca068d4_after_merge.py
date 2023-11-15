    def _get_level_indexer(self, key, level: int = 0, indexer=None):
        # `level` kwarg is _always_ positional, never name
        # return an indexer, boolean array or a slice showing where the key is
        # in the totality of values
        # if the indexer is provided, then use this

        level_index = self.levels[level]
        level_codes = self.codes[level]

        def convert_indexer(start, stop, step, indexer=indexer, codes=level_codes):
            # given the inputs and the codes/indexer, compute an indexer set
            # if we have a provided indexer, then this need not consider
            # the entire labels set

            r = np.arange(start, stop, step)
            if indexer is not None and len(indexer) != len(codes):

                # we have an indexer which maps the locations in the labels
                # that we have already selected (and is not an indexer for the
                # entire set) otherwise this is wasteful so we only need to
                # examine locations that are in this set the only magic here is
                # that the result are the mappings to the set that we have
                # selected
                from pandas import Series

                mapper = Series(indexer)
                indexer = codes.take(ensure_platform_int(indexer))
                result = Series(Index(indexer).isin(r).nonzero()[0])
                m = result.map(mapper)
                m = np.asarray(m)

            else:
                m = np.zeros(len(codes), dtype=bool)
                m[np.in1d(codes, r, assume_unique=Index(codes).is_unique)] = True

            return m

        if isinstance(key, slice):
            # handle a slice, returning a slice if we can
            # otherwise a boolean indexer

            try:
                if key.start is not None:
                    start = level_index.get_loc(key.start)
                else:
                    start = 0
                if key.stop is not None:
                    stop = level_index.get_loc(key.stop)
                elif isinstance(start, slice):
                    stop = len(level_index)
                else:
                    stop = len(level_index) - 1
                step = key.step
            except KeyError:

                # we have a partial slice (like looking up a partial date
                # string)
                start = stop = level_index.slice_indexer(
                    key.start, key.stop, key.step, kind="loc"
                )
                step = start.step

            if isinstance(start, slice) or isinstance(stop, slice):
                # we have a slice for start and/or stop
                # a partial date slicer on a DatetimeIndex generates a slice
                # note that the stop ALREADY includes the stopped point (if
                # it was a string sliced)
                start = getattr(start, "start", start)
                stop = getattr(stop, "stop", stop)
                return convert_indexer(start, stop, step)

            elif level > 0 or self.lexsort_depth == 0 or step is not None:
                # need to have like semantics here to right
                # searching as when we are using a slice
                # so include the stop+1 (so we include stop)
                return convert_indexer(start, stop + 1, step)
            else:
                # sorted, so can return slice object -> view
                i = level_codes.searchsorted(start, side="left")
                j = level_codes.searchsorted(stop, side="right")
                return slice(i, j, step)

        else:

            idx = self._get_loc_single_level_index(level_index, key)

            if level > 0 or self.lexsort_depth == 0:
                # Desired level is not sorted
                locs = np.array(level_codes == idx, dtype=bool, copy=False)
                if not locs.any():
                    # The label is present in self.levels[level] but unused:
                    raise KeyError(key)
                return locs

            if isinstance(idx, slice):
                start = idx.start
                end = idx.stop
            else:
                start = level_codes.searchsorted(idx, side="left")
                end = level_codes.searchsorted(idx, side="right")

            if start == end:
                # The label is present in self.levels[level] but unused:
                raise KeyError(key)
            return slice(start, end)