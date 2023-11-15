    def _get_time_bins(self, ax):
        if not isinstance(ax, DatetimeIndex):
            raise TypeError('axis must be a DatetimeIndex, but got '
                            'an instance of %r' % type(ax).__name__)

        if len(ax) == 0:
            binner = labels = DatetimeIndex(
                data=[], freq=self.freq, name=ax.name)
            return binner, [], labels

        first, last = ax.min(), ax.max()
        first, last = _get_range_edges(first, last, self.freq,
                                       closed=self.closed,
                                       base=self.base)
        tz = ax.tz
        # GH #12037
        # use first/last directly instead of call replace() on them
        # because replace() will swallow the nanosecond part
        # thus last bin maybe slightly before the end if the end contains
        # nanosecond part and lead to `Values falls after last bin` error
        binner = labels = DatetimeIndex(freq=self.freq,
                                        start=first,
                                        end=last,
                                        tz=tz,
                                        name=ax.name)

        # GH 15549
        # In edge case of tz-aware resapmling binner last index can be
        # less than the last variable in data object, this happens because of
        # DST time change
        if len(binner) > 1 and binner[-1] < last:
            extra_date_range = pd.date_range(binner[-1], last + self.freq,
                                             freq=self.freq, tz=tz,
                                             name=ax.name)
            binner = labels = binner.append(extra_date_range[1:])

        # a little hack
        trimmed = False
        if (len(binner) > 2 and binner[-2] == last and
                self.closed == 'right'):

            binner = binner[:-1]
            trimmed = True

        ax_values = ax.asi8
        binner, bin_edges = self._adjust_bin_edges(binner, ax_values)

        # general version, knowing nothing about relative frequencies
        bins = lib.generate_bins_dt64(
            ax_values, bin_edges, self.closed, hasnans=ax.hasnans)

        if self.closed == 'right':
            labels = binner
            if self.label == 'right':
                labels = labels[1:]
            elif not trimmed:
                labels = labels[:-1]
        else:
            if self.label == 'right':
                labels = labels[1:]
            elif not trimmed:
                labels = labels[:-1]

        if ax.hasnans:
            binner = binner.insert(0, NaT)
            labels = labels.insert(0, NaT)

        # if we end up with more labels than bins
        # adjust the labels
        # GH4076
        if len(bins) < len(labels):
            labels = labels[:len(bins)]

        return binner, bins, labels