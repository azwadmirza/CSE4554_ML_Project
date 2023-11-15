    def _get_index_loc(self, key, base_index=None):
        """
        Get the location of a specific key in an index

        Parameters
        ----------
        key : label
            The key for which to find the location
        base_index : pd.Index, optional
            Optionally the base index to search. If None, the model's index is
            searched.

        Returns
        -------
        loc : int
            The location of the key
        index : pd.Index
            The index including the key; this is a copy of the original index
            unless the index had to be expanded to accomodate `key`.
        index_was_expanded : bool
            Whether or not the index was expanded to accomodate `key`.

        Notes
        -----
        If `key` is past the end of of the given index, and the index is either
        an Int64Index or a date index, this function extends the index up to
        and including key, and then returns the location in the new index.

        """
        if base_index is None:
            base_index = self._index

        index = base_index
        date_index = isinstance(base_index, (PeriodIndex, DatetimeIndex))
        index_class = type(base_index)
        nobs = len(index)

        # Special handling for Int64Index
        if (isinstance(index, Int64Index) and not date_index and
                isinstance(key, (int, long, np.integer))):
            # Negative indices (that lie in the Index)
            if key < 0 and -key <= nobs:
                key = nobs + key
            # Out-of-sample (note that we include key itself in the new index)
            elif key > base_index[-1]:
                index = Int64Index(np.arange(base_index[0], int(key + 1)))

        # Special handling for date indexes
        if date_index:
            # Integer key (i.e. already given a location)
            if isinstance(key, (int, long, np.integer)):
                # Negative indices (that lie in the Index)
                if key < 0 and -key < nobs:
                    key = index[nobs + key]
                # Out-of-sample (note that we include key itself in the new
                # index)
                elif key > len(base_index) - 1:
                    index = index_class(start=base_index[0],
                                        periods=int(key + 1),
                                        freq=base_index.freq)
                    key = index[-1]
                else:
                    key = index[key]
            # Other key types (i.e. string date or some datetime-like object)
            else:
                # Covert the key to the appropriate date-like object
                if index_class is PeriodIndex:
                    date_key = Period(key, freq=base_index.freq)
                else:
                    date_key = Timestamp(key)

                # Out-of-sample
                if date_key > base_index[-1]:
                    # First create an index that may not always include `key`
                    index = index_class(start=base_index[0], end=date_key,
                                        freq=base_index.freq)

                    # Now make sure we include `key`
                    if not index[-1] == date_key:
                        index = index_class(start=base_index[0],
                                            periods=len(index) + 1,
                                            freq=base_index.freq)

        # Get the location (note that get_loc will throw a KeyError if key is
        # invalid)
        loc = index.get_loc(key)

        # Check if we now have a modified index
        index_was_expanded = index is not base_index

        # (Never return the actual index object)
        if not index_was_expanded:
            index = index.copy()

        # Return the index through the end of the loc / slice
        if isinstance(loc, slice):
            end = loc.stop
        else:
            end = loc

        return loc, index[:end + 1], index_was_expanded