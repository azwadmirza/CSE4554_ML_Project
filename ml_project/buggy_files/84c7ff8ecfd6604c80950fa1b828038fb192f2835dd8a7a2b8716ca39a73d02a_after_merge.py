    def __init__(self, n=1, normalize=False, week=0, weekday=0):
        self.n = self._validate_n(n)
        self.normalize = normalize
        self.weekday = weekday
        self.week = week

        if self.n == 0:
            raise ValueError('N cannot be 0')

        if self.weekday < 0 or self.weekday > 6:
            raise ValueError('Day must be 0<=day<=6, got {day}'
                             .format(day=self.weekday))
        if self.week < 0 or self.week > 3:
            raise ValueError('Week must be 0<=week<=3, got {week}'
                             .format(week=self.week))

        self.kwds = {'weekday': weekday, 'week': week}