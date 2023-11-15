    def __setitem__(self, key, value):
        """Set attribute corresponding to key with value."""
        try:
            setattr(self.__obj__, key, value)
        except TypeError:
            pass