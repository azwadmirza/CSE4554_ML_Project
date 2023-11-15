    def fit(self, X, y):
        """Fit Ridge regression model.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples,n_features]
            Training data

        y : array-like, shape = [n_samples]
            Target values

        Returns
        -------
        self : returns an instance of self.
        """
        self._label_binarizer = LabelBinarizer(pos_label=1, neg_label=-1)
        Y = self._label_binarizer.fit_transform(y)
        if not self._label_binarizer.y_type_.startswith('multilabel'):
            y = column_or_1d(y, warn=True)

        if self.class_weight:
            cw = compute_class_weight(self.class_weight,
                                      self.classes_, y)
            # get the class weight corresponding to each sample
            sample_weight = cw[np.searchsorted(self.classes_, y)]
        else:
            sample_weight = None

        super(RidgeClassifier, self).fit(X, Y, sample_weight=sample_weight)
        return self