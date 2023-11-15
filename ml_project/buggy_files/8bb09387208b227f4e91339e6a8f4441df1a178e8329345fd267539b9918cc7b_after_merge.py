    def get_value(self,
                  series: AnyArrayLike,
                  key: Any):
        """
        Fast lookup of value from 1-dimensional ndarray. Only use this if you
        know what you're doing

        Parameters
        ----------
        series : Series, ExtensionArray, Index, or ndarray
            1-dimensional array to take values from
        key: : scalar
            The value of this index at the position of the desired value,
            otherwise the positional index of the desired value

        Returns
        -------
        Any
            The element of the series at the position indicated by the key
        """
        try:
            k = com.values_from_object(key)
            k = self._convert_scalar_indexer(k, kind='getitem')
            indexer = self.get_loc(k)
            return series.take([indexer])[0]
        except (KeyError, TypeError):
            pass

        # we might be a positional inexer
        return super().get_value(series, key)