    def equals(self, other):
        """
        Determines if two Index objects contain the same elements.
        """
        if self is other:
            return True

        if (not hasattr(other, 'inferred_type') or
            other.inferred_type != 'datetime64'):
            if self.offset is not None:
                return False
            try:
                other = DatetimeIndex(other)
            except:
                return False

        if self.tz is not None:
            if other.tz is None:
                return False
            same_zone = self.tz.zone == other.tz.zone
        else:
            if other.tz is not None:
                return False
            same_zone = True

        return same_zone and np.array_equal(self.asi8, other.asi8)