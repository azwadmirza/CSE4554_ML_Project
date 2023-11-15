    def fit(self, X, y, sample_weight=None, class_weight=None):
        """Fit the ridge classifier.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.

        y : array-like, shape (n_samples,)
            Target values.

        sample_weight : float or numpy array of shape (n_samples,)
            Sample weight.

        class_weight : dict, optional
            Weights associated with classes in the form
            ``{class_label : weight}``. If not given, all classes are
            supposed to have weight one. This is parameter is
            deprecated.

        Returns
        -------
        self : object
            Returns self.
        """
        if class_weight is None:
            class_weight = self.class_weight
        else:
            warnings.warn("'class_weight' is now an initialization parameter."
                          " Using it in the 'fit' method is deprecated and "
                          "will be removed in 0.15.", DeprecationWarning,
                          stacklevel=2)
        if sample_weight is None:
            sample_weight = 1.

        self._label_binarizer = LabelBinarizer(pos_label=1, neg_label=-1)
        Y = self._label_binarizer.fit_transform(y)
        if not self._label_binarizer.y_type_.startswith('multilabel'):
            y = column_or_1d(y, warn=True)
        cw = compute_class_weight(class_weight,
                                  self.classes_, Y)
        # modify the sample weights with the corresponding class weight
        sample_weight *= cw[np.searchsorted(self.classes_, y)]
        _BaseRidgeCV.fit(self, X, Y, sample_weight=sample_weight)
        return self