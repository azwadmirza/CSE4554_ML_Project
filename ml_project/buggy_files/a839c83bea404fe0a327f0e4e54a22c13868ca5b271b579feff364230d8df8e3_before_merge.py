    def fit(self, X, y):
        """Fit estimator using RANSAC algorithm.

        Parameters
        ----------
        X : array-like or sparse matrix, shape [n_samples, n_features]
            Training data.

        y : array-like, shape = [n_samples] or [n_samples, n_targets]
            Target values.

        Raises
        ------
        ValueError
            If no valid consensus set could be found. This occurs if
            `is_data_valid` and `is_model_valid` return False for all
            `max_trials` randomly chosen sub-samples.

        """
        if self.base_estimator is not None:
            base_estimator = clone(self.base_estimator)
        else:
            base_estimator = LinearRegression()

        if self.min_samples is None:
            # assume linear model by default
            min_samples = X.shape[1] + 1
        elif 0 < self.min_samples < 1:
            min_samples = np.ceil(self.min_samples * X.shape[0])
        elif self.min_samples >= 1:
            if self.min_samples % 1 != 0:
                raise ValueError("Absolute number of samples must be an "
                                 "integer value.")
            min_samples = self.min_samples
        else:
            raise ValueError("Value for `min_samples` must be scalar and "
                             "positive.")
        if min_samples > X.shape[0]:
            raise ValueError("`min_samples` may not be larger than number "
                             "of samples ``X.shape[0]``.")

        if self.stop_probability < 0 or self.stop_probability > 1:
            raise ValueError("`stop_probability` must be in range [0, 1].")

        if self.residual_threshold is None:
            # MAD (median absolute deviation)
            residual_threshold = np.median(np.abs(y - np.median(y)))
        else:
            residual_threshold = self.residual_threshold

        if self.residual_metric is None:
            residual_metric = lambda dy: np.sum(np.abs(dy), axis=1)
        else:
            residual_metric = self.residual_metric

        random_state = check_random_state(self.random_state)

        try:  # Not all estimator accept a random_state
            base_estimator.set_params(random_state=random_state)
        except ValueError:
            pass

        n_inliers_best = 0
        score_best = np.inf
        inlier_mask_best = None
        X_inlier_best = None
        y_inlier_best = None

        # number of data samples
        n_samples = X.shape[0]
        sample_idxs = np.arange(n_samples)

        X = atleast2d_or_csr(X)
        y = np.asarray(y)

        if y.ndim == 1:
            y = y[:, None]

        for self.n_trials_ in range(1, self.max_trials + 1):

            # choose random sample set
            subset_idxs = sample_without_replacement(n_samples, min_samples,
                                                     random_state=random_state)
            X_subset = X[subset_idxs]
            y_subset = y[subset_idxs]

            # check if random sample set is valid
            if (self.is_data_valid is not None
                    and not self.is_data_valid(X_subset, y_subset)):
                continue

            # fit model for current random sample set
            base_estimator.fit(X_subset, y_subset)

            # check if estimated model is valid
            if (self.is_model_valid is not None and not
                    self.is_model_valid(base_estimator, X_subset, y_subset)):
                continue

            # residuals of all data for current random sample model
            y_pred = base_estimator.predict(X)
            if y_pred.ndim == 1:
                y_pred = y_pred[:, None]

            residuals_subset = residual_metric(y_pred - y)

            # classify data into inliers and outliers
            inlier_mask_subset = residuals_subset < residual_threshold
            n_inliers_subset = np.sum(inlier_mask_subset)

            # less inliers -> skip current random sample
            if n_inliers_subset < n_inliers_best:
                continue

            # extract inlier data set
            inlier_idxs_subset = sample_idxs[inlier_mask_subset]
            X_inlier_subset = X[inlier_idxs_subset]
            y_inlier_subset = y[inlier_idxs_subset]

            # score of inlier data set
            score_subset = base_estimator.score(X_inlier_subset,
                                                y_inlier_subset)

            # same number of inliers but worse score -> skip current random
            # sample
            if (n_inliers_subset == n_inliers_best
                    and score_subset < score_best):
                continue

            # save current random sample as best sample
            n_inliers_best = n_inliers_subset
            score_best = score_subset
            inlier_mask_best = inlier_mask_subset
            X_inlier_best = X_inlier_subset
            y_inlier_best = y_inlier_subset

            # break if sufficient number of inliers or score is reached
            if (n_inliers_best >= self.stop_n_inliers
                    or score_best >= self.stop_score
                    or self.n_trials_
                       >= _dynamic_max_trials(n_inliers_best, n_samples,
                                              min_samples,
                                              self.stop_probability)):
                break

        # if none of the iterations met the required criteria
        if inlier_mask_best is None:
            raise ValueError(
                "RANSAC could not find valid consensus set, because"
                " either the `residual_threshold` rejected all the samples or"
                " `is_data_valid` and `is_model_valid` returned False for all"
                " `max_trials` randomly ""chosen sub-samples. Consider "
                "relaxing the ""constraints.")

        # estimate final model using all inliers
        base_estimator.fit(X_inlier_best, y_inlier_best)

        self.estimator_ = base_estimator
        self.inlier_mask_ = inlier_mask_best
        return self