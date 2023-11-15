    def __getitem__(self, index_value):
        """
        Return copy NpTrace with sliced sample values if a slice is passed,
        or the array of samples if a varname is passed.
        """

        if isinstance(index_value, slice):

            sliced_trace = NpTrace(self.vars)
            sliced_trace.samples = dict((name, vals[index_value]) for (name, vals) in self.samples.items())

            return sliced_trace

        else:
            try:
                return self.point(index_value)
            except (ValueError, TypeError, IndexError):
                pass

            return self.samples[str(index_value)].value