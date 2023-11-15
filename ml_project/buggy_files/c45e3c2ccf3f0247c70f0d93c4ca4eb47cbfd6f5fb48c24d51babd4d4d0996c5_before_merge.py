    def predict_proba(self, X):
        """Probability estimates.
        Returns prediction probabilites for each class of each output.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Data

        Returns
        -------
        T : (sparse) array-like, shape = (n_samples, n_classes, n_outputs)
            The class probabilities of the samples for each of the outputs
        """
        check_is_fitted(self, 'estimators_')
        if not hasattr(self.estimator, "predict_proba"):
            raise ValueError("The base estimator should implement"
                             "predict_proba method")

        results = np.dstack([estimator.predict_proba(X) for estimator in
                            self.estimators_])
        return results