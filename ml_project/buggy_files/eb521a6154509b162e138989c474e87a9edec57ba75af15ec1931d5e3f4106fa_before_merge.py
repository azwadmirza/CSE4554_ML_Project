    def astype(self, col_dtypes):
        """Converts columns dtypes to given dtypes.

        Args:
            col_dtypes: Dictionary of {col: dtype,...} where col is the column
                name and dtype is a numpy dtype.

        Returns:
            dataframe with updated dtypes.
        """
        columns = col_dtypes.keys()
        # Create Series for the updated dtypes
        new_dtypes = self.dtypes.copy()
        for i, column in enumerate(columns):
            dtype = col_dtypes[column]
            if (
                not isinstance(dtype, type(self.dtypes[column]))
                or dtype != self.dtypes[column]
            ):
                # Update the new dtype series to the proper pandas dtype
                try:
                    new_dtype = np.dtype(dtype)
                except TypeError:
                    new_dtype = dtype
                if dtype != np.int32 and new_dtype == np.int32:
                    new_dtype = np.dtype("int64")
                elif dtype != np.float32 and new_dtype == np.float32:
                    new_dtype = np.dtype("float64")
                new_dtypes[column] = new_dtype
        # Update partitions for each dtype that is updated

        def astype_builder(df):
            return df.astype({k: v for k, v in col_dtypes.items() if k in df})

        new_frame = self._frame_mgr_cls.map_partitions(self._partitions, astype_builder)
        return self.__constructor__(
            new_frame,
            self.index,
            self.columns,
            self._row_lengths,
            self._column_widths,
            new_dtypes,
        )