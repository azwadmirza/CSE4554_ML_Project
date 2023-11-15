    def max_cycles(self, num):
        """
        Truncates all contained Cycle objects to a maximum number
        of Cycles and returns a new Options object with the
        truncated or resampled Cycles.
        """
        kwargs = {kw: (arg[num] if isinstance(arg, Cycle) else arg)
                  for kw, arg in self.kwargs.items()}
        return self(**kwargs)