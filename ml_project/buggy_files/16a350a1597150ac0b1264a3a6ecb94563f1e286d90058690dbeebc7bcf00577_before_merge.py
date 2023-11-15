    def _maybe_convert_index(self, data):
        # tsplot converts automatically, but don't want to convert index
        # over and over for DataFrames
        from pandas.core.frame import DataFrame
        if (isinstance(data.index, DatetimeIndex) and
            isinstance(data, DataFrame)):
            freq = getattr(data.index, 'freq', None)

            if freq is None:
                freq = getattr(data.index, 'inferred_freq', None)

            if isinstance(freq, DateOffset):
                freq = freq.rule_code

            freq = get_period_alias(freq)

            if freq is None:
                ax, _ = self._get_ax_and_style(0)
                freq = getattr(ax, 'freq', None)

            if freq is None:
                raise ValueError('Could not get frequency alias for plotting')

            data = DataFrame(data.values,
                             index=data.index.to_period(freq=freq),
                             columns=data.columns)
        return data