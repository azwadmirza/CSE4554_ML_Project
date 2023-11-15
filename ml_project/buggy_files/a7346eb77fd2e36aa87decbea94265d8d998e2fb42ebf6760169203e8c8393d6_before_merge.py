    def rollforward(self, dt):
        """Roll provided date forward to next offset only if not on offset"""
        if not self.onOffset(dt):
            dt = dt + self.__class__(1, **self.kwds)
        return dt