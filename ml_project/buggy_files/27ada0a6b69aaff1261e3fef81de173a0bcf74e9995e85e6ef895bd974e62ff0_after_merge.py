    def max_cycles(self, num):
        """
        Truncates all contained Palette objects to a maximum number
        of samples and returns a new Options object containing the
        truncated or resampled Palettes.
        """
        kwargs = {kw: (arg[num] if isinstance(arg, Palette) else arg)
                  for kw, arg in self.kwargs.items()}
        return self(max_cycles=num, **kwargs)