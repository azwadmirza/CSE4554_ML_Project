def gethash(self):
    if not getattr(self, '_cachedhash', None):
        spec = inspect.getargspec(self.__init__)
        valuetuple = tuple([getattr(self, x, None) for x in spec.args if x != 'self'])
        self._cachedhash = hash(valuetuple)
    return self._cachedhash