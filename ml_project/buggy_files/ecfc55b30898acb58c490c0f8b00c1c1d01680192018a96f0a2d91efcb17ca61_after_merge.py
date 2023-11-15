    def __repr__(self):
        from pandas.core.format import _format_datetime64
        values = self.values

        freq = None
        if self.offset is not None:
            freq = self.offset.freqstr

        summary = str(self.__class__)
        if len(self) == 1:
            first = _format_datetime64(values[0], tz=self.tz)
            summary += '\n[%s]' % first
        elif len(self) == 2:
            first = _format_datetime64(values[0], tz=self.tz)
            last = _format_datetime64(values[-1], tz=self.tz)
            summary += '\n[%s, %s]' % (first, last)
        elif len(self) > 2:
            first = _format_datetime64(values[0], tz=self.tz)
            last = _format_datetime64(values[-1], tz=self.tz)
            summary += '\n[%s, ..., %s]' % (first, last)

        tagline = '\nLength: %d, Freq: %s, Timezone: %s'
        summary += tagline % (len(self), freq, self.tz)

        return summary