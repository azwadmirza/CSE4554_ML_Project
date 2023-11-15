    def _iter_indices(self, X, y, groups):
        if groups is None:
            raise ValueError("The groups parameter should not be None")
        groups = check_array(groups, ensure_2d=False, dtype=None)
        classes, group_indices = np.unique(groups, return_inverse=True)
        for group_train, group_test in super(
                GroupShuffleSplit, self)._iter_indices(X=classes):
            # these are the indices of classes in the partition
            # invert them into data indices

            train = np.flatnonzero(np.in1d(group_indices, group_train))
            test = np.flatnonzero(np.in1d(group_indices, group_test))

            yield train, test