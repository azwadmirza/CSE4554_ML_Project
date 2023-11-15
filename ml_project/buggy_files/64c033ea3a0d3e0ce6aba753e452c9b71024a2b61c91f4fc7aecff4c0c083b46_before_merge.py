    def decision_function(self, X):
        """Decision function for the OneVsOneClassifier.

        The decision values for the samples are computed by adding the 
        normalized sum of pair-wise classification confidence levels to the
        votes in order to disambiguate between the decision values when the
        votes for all the classes are equal leading to a tie.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]

        Returns
        -------
        Y : array-like, shape = [n_samples, n_classes]
        """
        check_is_fitted(self, 'estimators_')

        n_samples = X.shape[0]
        n_classes = self.classes_.shape[0]
        votes = np.zeros((n_samples, n_classes))
        sum_of_confidences = np.zeros((n_samples, n_classes))

        k = 0
        for i in range(n_classes):
            for j in range(i + 1, n_classes):
                pred = self.estimators_[k].predict(X)
                confidence_levels_ij = _predict_binary(self.estimators_[k], X)
                sum_of_confidences[:, i] -= confidence_levels_ij
                sum_of_confidences[:, j] += confidence_levels_ij
                votes[pred == 0, i] += 1
                votes[pred == 1, j] += 1
                k += 1

        max_confidences = sum_of_confidences.max()
        min_confidences = sum_of_confidences.min()

        if max_confidences == min_confidences:
            return votes

        # Scale the sum_of_confidences to [-0.4, 0.4] and add it with votes
        return votes + sum_of_confidences * \
               (0.4 / max(abs(max_confidences), abs(min_confidences)))