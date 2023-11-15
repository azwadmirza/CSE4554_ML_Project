    def __init__(self, distribution, lower, upper, transform='infer', *args, **kwargs):
        self.dist = distribution.dist(*args, **kwargs)
        self.__dict__.update(self.dist.__dict__)
        self.__dict__.update(locals())

        if hasattr(self.dist, 'mode'):
            self.mode = self.dist.mode

        if transform == 'infer':
            self.transform, self.testval = self._infer(lower, upper)