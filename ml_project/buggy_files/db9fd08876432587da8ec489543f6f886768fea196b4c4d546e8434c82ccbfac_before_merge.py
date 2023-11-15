    def __setitem__(self, key, value):
        """Set attribute corresponding to key with value."""
        # Catch AttributeError to gracefully handle inability to set an
        # attribute due to it not being writeable or set-table.
        # Fix issue #6728 . Also, catch NotImplementedError for safety.
        try:
            setattr(self.__obj__, key, value)
        except (TypeError, AttributeError, NotImplementedError):
            pass