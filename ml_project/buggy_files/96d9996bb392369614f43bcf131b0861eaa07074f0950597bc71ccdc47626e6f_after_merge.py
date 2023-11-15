    def __getattr__(self, key):
        # TODO keep this for a version, in order to not break old code
        # this entire method (as well as the _dict attribute in __slots__ and the __setattr__ method)
        # can be removed in 4.0
        # this method is only called if the attribute was not found elsewhere, like in __slots_
        if key not in self.__slots__:
            raise AttributeError
        try:
            warnings.warn("Custom attributes of messages are deprecated and will be removed in 4.0", DeprecationWarning)
            return self._dict[key]
        except KeyError:
            raise AttributeError("'message' object has no attribute '{}'".format(key))