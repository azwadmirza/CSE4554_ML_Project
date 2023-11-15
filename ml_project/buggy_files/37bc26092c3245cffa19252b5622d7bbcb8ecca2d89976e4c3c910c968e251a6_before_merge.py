    def inverse_transform(self, yt):
        """Transform the given indicator matrix into label sets

        Parameters
        ----------
        yt : array of shape (n_samples, n_classes)
            A matrix containing only 1s ands 0s.

        Returns
        -------
        y : list of tuples
            The set of labels for each sample such that `y[i]` consists of
            `classes_[j]` for each `yt[i, j] == 1`.
        """
        yt = np.asarray(yt)
        if yt.shape[1] != len(self.classes_):
            raise ValueError('Expected indicator for {0} classes, but got {1}'
                             .format(len(self.classes_), yt.shape[1]))
        unexpected = np.setdiff1d(yt, [0, 1])
        if len(unexpected) > 0:
            raise ValueError('Expected only 0s and 1s in label indicator. '
                             'Also got {0}'.format(unexpected))

        return [tuple(self.classes_.compress(indicators)) for indicators in yt]