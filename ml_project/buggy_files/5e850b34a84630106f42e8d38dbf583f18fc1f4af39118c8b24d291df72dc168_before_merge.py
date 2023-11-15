    def insert(self, loc, item):
        """
        Make new Index inserting new item at location

        Parameters
        ----------
        loc : int
        item : object
            if not either a Python datetime or a numpy integer-like, returned
            Index dtype will be object rather than datetime.

        Returns
        -------
        new_index : Index
        """

        freq = None
        if isinstance(item, (datetime, np.datetime64)):
            zone = tslib.get_timezone(self.tz)
            izone = tslib.get_timezone(getattr(item, 'tzinfo', None))
            if zone != izone:
                raise ValueError('Passed item and index have different timezone')
            # check freq can be preserved on edge cases
            if self.freq is not None:
                if (loc == 0 or loc == -len(self)) and item + self.freq == self[0]:
                    freq = self.freq
                elif (loc == len(self)) and item - self.freq == self[-1]:
                    freq = self.freq
            item = _to_m8(item, tz=self.tz)
        try:
            new_dates = np.concatenate((self[:loc].asi8, [item.view(np.int64)],
                                        self[loc:].asi8))
            if self.tz is not None:
                new_dates = tslib.tz_convert(new_dates, 'UTC', self.tz)
            return DatetimeIndex(new_dates, name=self.name, freq=freq, tz=self.tz)

        except (AttributeError, TypeError):

            # fall back to object index
            if isinstance(item,compat.string_types):
                return self.asobject.insert(loc, item)
            raise TypeError("cannot insert DatetimeIndex with incompatible label")