    def set_index(self, col_or_cols, drop=True, inplace=False):
        """
        Set the DataFrame index (row labels) using one or more existing
        columns. By default yields a new object.

        Parameters
        ----------
        col_or_cols : column label or list of column labels
        drop : boolean, default True
            Delete columns to be used as the new index
        inplace : boolean, default False
            Modify the DataFrame in place (do not create a new object)

        Returns
        -------
        dataframe : DataFrame
        """
        cols = col_or_cols
        if not isinstance(col_or_cols, (list, tuple)):
            cols = [col_or_cols]

        if inplace:
            frame = self

        else:
            frame = self.copy()

        arrays = []
        for col in cols:
            level = frame[col]
            if drop:
                del frame[col]
            arrays.append(level)

        index = MultiIndex.from_arrays(arrays, names=cols)

        if not index._verify_integrity():
            duplicates = index._get_duplicates()
            raise Exception('Index has duplicate keys: %s' % duplicates)

        # clear up memory usage
        index._cleanup()

        frame.index = index
        return frame