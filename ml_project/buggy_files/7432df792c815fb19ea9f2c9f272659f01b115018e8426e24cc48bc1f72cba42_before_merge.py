    def fit(self, X, y):
        """Fit the RFE model and automatically tune the number of selected
           features.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vector, where `n_samples` is the number of samples and
            `n_features` is the total number of features.

        y : array-like, shape = [n_samples]
            Target values (integers for classification, real numbers for
            regression).
        """
        X, y = check_X_y(X, y, "csr")
        # Initialization
        rfe = RFE(estimator=self.estimator, n_features_to_select=1,
                  step=self.step, estimator_params=self.estimator_params,
                  verbose=self.verbose - 1)

        cv = check_cv(self.cv, X, y, is_classifier(self.estimator))
        scorer = check_scoring(self.estimator, scoring=self.scoring)
        scores = np.zeros(X.shape[1])
        n_features_to_select_by_rank = np.zeros(X.shape[1])

        # Cross-validation
        for n, (train, test) in enumerate(cv):
            X_train, y_train = _safe_split(self.estimator, X, y, train)
            X_test, y_test = _safe_split(self.estimator, X, y, test, train)

            # Compute a full ranking of the features
            # ranking_ contains the same set of values for all CV folds,
            # but perhaps reordered
            ranking_ = rfe.fit(X_train, y_train).ranking_
            # Score each subset of features
            for k in range(0, np.max(ranking_)):
                indices = np.where(ranking_ <= k + 1)[0]
                estimator = clone(self.estimator)
                estimator.fit(X_train[:, indices], y_train)
                score = _score(estimator, X_test[:, indices], y_test, scorer)

                if self.verbose > 0:
                    print("Finished fold with %d / %d feature ranks, score=%f"
                          % (k + 1, np.max(ranking_), score))
                scores[k] += score
                # n_features_to_select_by_rank[k] is being overwritten
                # multiple times, but by the same value
                n_features_to_select_by_rank[k] = indices.size

        # Select the best upper bound for feature rank. It's OK to use the
        # last ranking_, as np.max(ranking_) is the same over all CV folds.
        scores = scores[:np.max(ranking_)]
        k = np.argmax(scores)

        # Re-execute an elimination with best_k over the whole set
        rfe = RFE(estimator=self.estimator,
                  n_features_to_select=n_features_to_select_by_rank[k],
                  step=self.step, estimator_params=self.estimator_params)

        rfe.fit(X, y)

        # Set final attributes
        self.support_ = rfe.support_
        self.n_features_ = rfe.n_features_
        self.ranking_ = rfe.ranking_
        self.estimator_ = clone(self.estimator)
        self.estimator_.set_params(**self.estimator_params)
        self.estimator_.fit(self.transform(X), y)

        # Fixing a normalization error, n is equal to len(cv) - 1
        # here, the scores are normalized by len(cv)
        self.grid_scores_ = scores / len(cv)
        return self