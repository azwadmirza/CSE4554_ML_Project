    def rollback(self, someDate):
        """Roll provided date backward to next offset only if not on offset"""
        if not self.onOffset(someDate):
            someDate = someDate - self.__class__(1, **self.kwds)
        return someDate