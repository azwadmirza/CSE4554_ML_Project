    def to_records(self, index=True, convert_datetime64=True):
        """
        Convert DataFrame to record array. Index will be put in the
        'index' field of the record array if requested

        Parameters
        ----------
        index : boolean, default True
            Include index in resulting record array, stored in 'index' field
        convert_datetime64 : boolean, default True
            Whether to convert the index to datetime.datetime if it is a
            DatetimeIndex

        Returns
        -------
        y : recarray
        """
        if index:
            if is_datetime64_dtype(self.index) and convert_datetime64:
                ix_vals = [self.index.to_pydatetime()]
            else:
                if isinstance(self.index, MultiIndex):
                    # array of tuples to numpy cols. copy copy copy
                    ix_vals = lmap(np.array, zip(*self.index.values))
                else:
                    ix_vals = [self.index.values]

            arrays = ix_vals + [self[c].get_values() for c in self.columns]

            count = 0
            index_names = list(self.index.names)
            if isinstance(self.index, MultiIndex):
                for i, n in enumerate(index_names):
                    if n is None:
                        index_names[i] = 'level_%d' % count
                        count += 1
            elif index_names[0] is None:
                index_names = ['index']
            names = lmap(str, index_names) + lmap(str, self.columns)
        else:
            arrays = [self[c].get_values() for c in self.columns]
            names = lmap(str, self.columns)

        dtype = np.dtype([(x, v.dtype) for x, v in zip(names, arrays)])
        return np.rec.fromarrays(arrays, dtype=dtype, names=names)