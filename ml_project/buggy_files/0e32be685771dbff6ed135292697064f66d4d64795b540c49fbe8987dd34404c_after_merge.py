    def _groupby_and_aggregate(self, grouper, how, *args, **kwargs):
        if grouper is None:
            return self._downsample(how, **kwargs)
        return super(PeriodIndexResampler, self)._groupby_and_aggregate(
            grouper, how, *args, **kwargs)