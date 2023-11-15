    def to_hierarchical(self, n_repeat, n_shuffle=1):
        """
        Return a MultiIndex reshaped to conform to the
        shapes given by n_repeat and n_shuffle.

        Useful to replicate and rearrange a MultiIndex for combination
        with another Index with n_repeat items.

        Parameters
        ----------
        n_repeat : int
            Number of times to repeat the labels on self
        n_shuffle : int
            Controls the reordering of the labels. If the result is going
            to be an inner level in a MultiIndex, n_shuffle will need to be
            greater than one. The size of each label must divisible by
            n_shuffle.

        Returns
        -------
        MultiIndex

        Examples
        --------
        >>> idx = MultiIndex.from_tuples([(1, u'one'), (1, u'two'),
                                          (2, u'one'), (2, u'two')])
        >>> idx.to_hierarchical(3)
        MultiIndex(levels=[[1, 2], [u'one', u'two']],
                   labels=[[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                           [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1]])
        """
        levels = self.levels
        labels = [np.repeat(x, n_repeat) for x in self.labels]
        # Assumes that each label is divisible by n_shuffle
        labels = [x.reshape(n_shuffle, -1).ravel('F') for x in labels]
        names = self.names
        return MultiIndex(levels=levels, labels=labels, names=names)