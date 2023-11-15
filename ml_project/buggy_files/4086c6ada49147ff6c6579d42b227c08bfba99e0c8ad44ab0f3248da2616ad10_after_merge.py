    def get_loc(self, key):
        """
        Get integer location for requested label

        Returns
        -------
        loc : int
        """
        try:
            return self._engine.get_loc(key)
        except KeyError:
            try:
                return self._get_string_slice(key)
            except (TypeError, KeyError):
                pass

            if isinstance(key, time):
                return self._indices_at_time(key)

            stamp = Timestamp(key)
            try:
                return self._engine.get_loc(stamp)
            except KeyError:
                raise KeyError(stamp)