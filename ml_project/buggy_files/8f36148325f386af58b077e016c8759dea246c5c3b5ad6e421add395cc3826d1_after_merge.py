    def update(self, other):
        """
        Modify Series in place using non-NA values from passed
        Series. Aligns on index.

        Parameters
        ----------
        other : Series, or object coercible into Series
        """
        if not isinstance(other, Series):
            other = Series(other)
        query_compiler = self._query_compiler.series_update(other._query_compiler)
        self._update_inplace(new_query_compiler=query_compiler)