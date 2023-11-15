    def __repr__(self):
        return "{0}.{1}(...)".format(  # noqa F523
            self.__class__.__module__, self.__class__.__name__, self._d
        )