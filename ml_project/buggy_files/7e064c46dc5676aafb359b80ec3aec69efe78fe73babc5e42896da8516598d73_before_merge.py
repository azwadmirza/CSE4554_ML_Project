    def _python_apply_general(
        self, f: F, data: FrameOrSeriesUnion
    ) -> FrameOrSeriesUnion:
        """
        Apply function f in python space

        Parameters
        ----------
        f : callable
            Function to apply
        data : Series or DataFrame
            Data to apply f to

        Returns
        -------
        Series or DataFrame
            data after applying f
        """
        keys, values, mutated = self.grouper.apply(f, data, self.axis)

        return self._wrap_applied_output(
            keys, values, not_indexed_same=mutated or self.mutated
        )