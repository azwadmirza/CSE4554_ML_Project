    def get_value(self, series, key):
        """
        Fast lookup of value from 1-dimensional ndarray. Only use this if you
        know what you're doing
        """
        try:
            return Index.get_value(self, series, key)
        except KeyError:

            try:
                loc = self._get_string_slice(key)
                return series[loc]
            except (TypeError, ValueError, KeyError):
                pass

            if isinstance(key, time):
                locs = self.indexer_at_time(key)
                return series.take(locs)

            if isinstance(key, basestring):
                stamp = Timestamp(key, tz=self.tz)
            else:
                stamp = Timestamp(key)
            try:
                return self._engine.get_value(series, stamp)
            except KeyError:
                raise KeyError(stamp)