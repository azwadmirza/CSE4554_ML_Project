    def __init__(self, n=1, normalize=False, weekday=None):
        self.n = self._validate_n(n)
        self.normalize = normalize
        self.weekday = weekday

        if self.n == 0:
            raise ValueError('N cannot be 0')

        if self.weekday < 0 or self.weekday > 6:
            raise ValueError('Day must be 0<=day<=6, got {day}'
                             .format(day=self.weekday))

        self.kwds = {'weekday': weekday}