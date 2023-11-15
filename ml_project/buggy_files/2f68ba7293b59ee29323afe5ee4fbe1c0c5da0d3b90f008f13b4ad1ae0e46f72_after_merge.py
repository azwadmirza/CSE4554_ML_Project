    def _maybe_cast_for_get_loc(self, key) -> Timestamp:
        # needed to localize naive datetimes or dates (GH 35690)
        key = Timestamp(key)
        if key.tzinfo is None:
            key = key.tz_localize(self.tz)
        else:
            key = key.tz_convert(self.tz)
        return key