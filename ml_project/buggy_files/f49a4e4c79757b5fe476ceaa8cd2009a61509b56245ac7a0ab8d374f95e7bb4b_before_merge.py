    def __getitem__(self, key):
        """Get the attribute corresponding to given key."""
        # Fix #6284 where pandas MultiIndex returns NotImplementedError
        # Due to NA checking not being supported on a multiindex.
        try:
            attribute_toreturn = getattr(self.__obj__, key)
        except NotImplementedError:
            attribute_toreturn = None
        return attribute_toreturn