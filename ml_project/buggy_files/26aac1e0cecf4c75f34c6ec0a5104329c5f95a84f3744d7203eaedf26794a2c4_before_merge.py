    def __init__(self, distribution, lower, upper, transform='infer', *args, **kwargs):
        self.dist = distribution.dist(*args, **kwargs)

        self.__dict__.update(self.dist.__dict__)
        self.__dict__.update(locals())

        if hasattr(self.dist, 'mode'):
            self.mode = self.dist.mode

        if transform == 'infer':

            default = self.dist.default()

            if not np.isinf(lower) and not np.isinf(upper):
                self.transform = transforms.interval(lower, upper)
                if default <= lower or default >= upper:
                    self.testval = 0.5 * (upper + lower)

            if not np.isinf(lower) and np.isinf(upper):
                self.transform = transforms.lowerbound(lower)
                if default <= lower:
                    self.testval = lower + 1

            if np.isinf(lower) and not np.isinf(upper):
                self.transform = transforms.upperbound(upper)
                if default >= upper:
                    self.testval = upper - 1