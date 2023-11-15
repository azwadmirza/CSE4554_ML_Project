    def dtype(self):
        if self.calendar is None or self.calendar in _STANDARD_CALENDARS:
            # TODO: return the proper dtype (object) for a standard calendar
            # that can't be expressed in ns precision. Perhaps we could guess
            # this from the units?
            return np.dtype('datetime64[ns]')
        else:
            return np.dtype('O')