    def rollforward(self, dt):
        """Roll provided date forward to next offset only if not on offset"""
        if type(dt) == date:
            dt = datetime(dt.year, dt.month, dt.day)

        if not self.onOffset(dt):
            dt = dt + self.__class__(1, **self.kwds)
        return dt