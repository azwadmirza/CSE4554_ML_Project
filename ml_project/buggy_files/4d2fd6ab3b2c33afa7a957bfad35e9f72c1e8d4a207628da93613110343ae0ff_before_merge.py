    def fit(self, y):
        """Fit the label sets binarizer, storing classes_

        Parameters
        ----------
        y : iterable of iterables
            A set of labels (any orderable and hashable object) for each
            sample. If the `classes` parameter is set, `y` will not be
            iterated.

        Returns
        -------
        self : returns this MultiLabelBinarizer instance
        """
        if self.classes is None:
            classes = sorted(set(itertools.chain.from_iterable(y)))
        else:
            classes = self.classes
        dtype = np.int if all(isinstance(c, int) for c in classes) else object
        self.classes_ = np.empty(len(classes), dtype=dtype)
        self.classes_[:] = classes
        return self