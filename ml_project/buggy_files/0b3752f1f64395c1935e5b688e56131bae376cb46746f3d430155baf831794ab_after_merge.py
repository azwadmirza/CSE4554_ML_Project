def gethash(self):
    if not getattr(self, '_cachedhash', None):
        spec = inspect.getargspec(self.__init__)
        valuetuple = tuple(
            map(lambda v: v if not isinstance(v, list) else str(v), [
                getattr(self, x, None) for x in spec.args if x != 'self'
            ])
        )
        self._cachedhash = hash(valuetuple)
    return self._cachedhash