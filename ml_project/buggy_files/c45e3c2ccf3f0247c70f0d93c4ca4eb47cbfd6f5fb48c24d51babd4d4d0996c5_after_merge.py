    def predict_proba(self, X):
        """Probability estimates.
        Returns prediction probabilites for each class of each output.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Data

        Returns
        -------
        p : array of shape = [n_samples, n_classes], or a list of n_outputs \
            such arrays if n_outputs > 1.
            The class probabilities of the input samples. The order of the
            classes corresponds to that in the attribute `classes_`.
        """
        check_is_fitted(self, 'estimators_')
        if not hasattr(self.estimator, "predict_proba"):
            raise ValueError("The base estimator should implement"
                             "predict_proba method")

        results = [estimator.predict_proba(X) for estimator in
                   self.estimators_]
        return results