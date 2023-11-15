    def map(self, mapper):
        """
        Apply mapper function to its values.

        Parameters
        ----------
        mapper : callable
            Function to be applied.

        Returns
        -------
        applied : array
        """
        return self._arrmap(self.values, mapper)