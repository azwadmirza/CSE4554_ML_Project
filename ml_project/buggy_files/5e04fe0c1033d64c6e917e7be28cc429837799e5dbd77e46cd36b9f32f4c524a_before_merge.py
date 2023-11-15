    def __call__(self, *args, **kwargs):
        if 'observed' in kwargs:
            raise ValueError('Observed Bound distributions are not supported. '
                             'If you want to model truncated data '
                             'you can use a pm.Potential in combination '
                             'with the cumulative probability function. See '
                             'pymc3/examples/censored_data.py for an example.')
        first, args = args[0], args[1:]

        if issubclass(self.distribution, Continuous):
            return _ContinuousBounded(first, self.distribution,
                                      self.lower, self.upper, *args, **kwargs)
        elif issubclass(self.distribution, Discrete):
            return _DiscreteBounded(first, self.distribution,
                                    self.lower, self.upper, *args, **kwargs)
        else:
            raise ValueError('Distribution is neither continuous nor discrete.')