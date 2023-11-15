    def reindex(self, major=None, items=None, minor=None, major_axis=None,
                minor_axis=None, copy=False):
        """
        Conform / reshape panel axis labels to new input labels

        Parameters
        ----------
        major : array-like, default None
        items : array-like, default None
        minor : array-like, default None
        copy : boolean, default False
            Copy underlying SparseDataFrame objects

        Returns
        -------
        reindexed : SparsePanel
        """
        major = _mut_exclusive(major, major_axis)
        minor = _mut_exclusive(minor, minor_axis)

        if None == major == items == minor:
            raise ValueError('Must specify at least one axis')

        major = self.major_axis if major is None else major
        minor = self.minor_axis if minor is None else minor

        if items is not None:
            new_frames = {}
            for item in items:
                if item in self._frames:
                    new_frames[item] = self._frames[item]
                else:
                    raise Exception('Reindexing with new items not yet '
                                    'supported')
        else:
            new_frames = self._frames

        if copy:
            new_frames = dict((k, v.copy()) for k, v in new_frames.iteritems())

        return SparsePanel(new_frames, items=items,
                           major_axis=major,
                           minor_axis=minor,
                           default_fill_value=self.default_fill_value,
                           default_kind=self.default_kind)