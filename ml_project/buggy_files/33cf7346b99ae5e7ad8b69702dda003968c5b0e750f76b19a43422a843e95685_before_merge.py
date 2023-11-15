    def class_gradient(self, x, label=None, **kwargs):
        """
        Compute per-class derivatives w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param label: Index of a specific per-class derivative. If `None`, then gradients for all
                      classes will be computed.
        :type label: `int`
        :param raw: Return the individual classifier raw outputs (not aggregated).
        :type raw: `bool`
        :return: Array of gradients of input features w.r.t. each class in the form
                 `(batch_size, nb_classes, input_shape)` when computing for all classes, otherwise shape becomes
                 `(batch_size, 1, input_shape)` when `label` parameter is specified. If `raw=True`, an additional
                 dimension is added at the beginning of the array, indexing the different classifiers.
        :rtype: `np.ndarray`
        """
        if 'raw' in kwargs:
            raw = kwargs['raw']
        else:
            raise ValueError('Missing argument `raw`.')

        grads = np.array([self._classifier_weights[i] * self._classifiers[i].class_gradient(x, label)
                          for i in range(self._nb_classifiers)])
        if raw:
            return grads
        return np.sum(grads, axis=0)