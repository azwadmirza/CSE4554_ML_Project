    def _get_new_index(self):
        """ return our new index """
        ax = self.ax
        ax_attrs = ax._get_attributes_dict()
        ax_attrs['freq'] = self.freq
        obj = self._selected_obj

        if len(ax) == 0:
            new_index = PeriodIndex(data=[], **ax_attrs)
            return obj.reindex(new_index)

        start = ax[0].asfreq(self.freq, how=self.convention)
        end = ax[-1].asfreq(self.freq, how='end')

        return period_range(start, end, **ax_attrs)