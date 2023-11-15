    def fit(self, X, y):
        """Fit the model using X as training data and y as target values

        Parameters
        ----------
        X : sktime-format pandas dataframe with shape([n_cases,n_dimensions]),
        or numpy ndarray with shape([n_cases,n_readings,n_dimensions])

        y : {array-like, sparse matrix}
            Target values of shape = [n_samples]

        """
        X, y = check_X_y(X, y, enforce_univariate=False, coerce_to_numpy=True)
        y = np.asarray(y)
        check_classification_targets(y)

        # print(X)
        # if internal cv is desired, the relevant flag forces a grid search
        # to evaluate the possible values,
        # find the best, and then set this classifier's params to match
        if self._cv_for_params:
            grid = GridSearchCV(
                estimator=KNeighborsTimeSeriesClassifier(
                    metric=self.metric, n_neighbors=1, algorithm="brute"
                ),
                param_grid=self._param_matrix,
                cv=LeaveOneOut(),
                scoring="accuracy",
            )
            grid.fit(X, y)
            self.metric_params = grid.best_params_["metric_params"]

        if y.ndim == 1 or y.ndim == 2 and y.shape[1] == 1:
            if y.ndim != 1:
                warnings.warn(
                    "IN TS-KNN: A column-vector y was passed when a 1d array "
                    "was expected. Please change the shape of y to "
                    "(n_samples, ), for example using ravel().",
                    DataConversionWarning,
                    stacklevel=2,
                )

            self.outputs_2d_ = False
            y = y.reshape((-1, 1))
        else:
            self.outputs_2d_ = True

        self.classes_ = []
        self._y = np.empty(y.shape, dtype=np.int)
        for k in range(self._y.shape[1]):
            classes, self._y[:, k] = np.unique(y[:, k], return_inverse=True)
            self.classes_.append(classes)

        if not self.outputs_2d_:
            self.classes_ = self.classes_[0]
            self._y = self._y.ravel()

        if hasattr(check_array, "__wrapped__"):
            temp = check_array.__wrapped__.__code__
            check_array.__wrapped__.__code__ = _check_array_ts.__code__
        else:
            temp = check_array.__code__
            check_array.__code__ = _check_array_ts.__code__

        fx = self._fit(X, self._y)

        if hasattr(check_array, "__wrapped__"):
            check_array.__wrapped__.__code__ = temp
        else:
            check_array.__code__ = temp

        self._is_fitted = True
        return fx