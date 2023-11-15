    def _sub_datelike(self, other):
        raise TypeError("cannot subtract a datelike from a TimedeltaIndex")