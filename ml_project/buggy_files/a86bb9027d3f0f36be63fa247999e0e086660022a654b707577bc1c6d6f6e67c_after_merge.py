    def resample(self, rule, how=None, axis=0, fill_method=None,
                 closed='right', label='right', convention=None,
                 kind=None, loffset=None, limit=None, base=0):
        """
        Convenience method for frequency conversion and resampling of regular
        time-series data.

        Parameters
        ----------
        rule : the offset string or object representing target conversion
        how : string, method for down- or re-sampling, default to 'mean' for
              downsampling
        fill_method : string, fill_method for upsampling, default None
        axis : int, optional, default 0
        closed : {'right', 'left'}, default 'right'
            Which side of bin interval is closed
        label : {'right', 'left'}, default 'right'
            Which bin edge label to label bucket with
        convention : {'start', 'end', 's', 'e'}
        loffset : timedelta
            Adjust the resampled time labels
        base : int, default 0
            For frequencies that evenly subdivide 1 day, the "origin" of the
            aggregated intervals. For example, for '5min' frequency, base could
            range from 0 through 4. Defaults to 0
        """
        from pandas.tseries.resample import TimeGrouper
        sampler = TimeGrouper(rule, label=label, closed=closed, how=how,
                              axis=axis, kind=kind, loffset=loffset,
                              fill_method=fill_method, convention=convention,
                              limit=limit, base=base)
        return sampler.resample(self)