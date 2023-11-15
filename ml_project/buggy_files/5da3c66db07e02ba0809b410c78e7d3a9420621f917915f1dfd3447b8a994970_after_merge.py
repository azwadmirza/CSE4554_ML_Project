    def evaluate_defence(self, is_clean, **kwargs):
        """
        Returns confusion matrix.

        :param is_clean: ground truth, where is_clean[i]=1 means that x_train[i] is clean and is_clean[i]=0 means
                         x_train[i] is poisonous
        :type is_clean: :class `list`
        :param kwargs: a dictionary of defence-specific parameters
        :type kwargs: `dict`
        :return: JSON object with confusion matrix
        :rtype: `jsonObject`
        """
        self.set_params(**kwargs)

        if not self.activations_by_class:
            activations = self._get_activations()
            self.activations_by_class = self._segment_by_class(activations, self.y_train)

        self.clusters_by_class, self.red_activations_by_class = self.cluster_activations()
        report, self.assigned_clean_by_class = self.analyze_clusters()

        # Now check ground truth:
        self.is_clean_by_class = self._segment_by_class(is_clean, self.y_train)
        self.errors_by_class, conf_matrix_json = self.evaluator.analyze_correctness(self.assigned_clean_by_class,
                                                                                    self.is_clean_by_class)
        return conf_matrix_json