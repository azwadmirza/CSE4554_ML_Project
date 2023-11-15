    def loss_gradient(self, x, y, raw=False, **kwargs):
        """
        Compute the gradient of the loss function w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param y: Target values (class labels) one-hot-encoded of shape (nb_samples, nb_classes) or indices of shape
                  (nb_samples,).
        :type y: `np.ndarray`
        :param raw: Return the individual classifier raw outputs (not aggregated).
        :type raw: `bool`
        :return: Array of gradients of the same shape as `x`. If `raw=True`, shape becomes `[nb_classifiers, x.shape]`.
        :rtype: `np.ndarray`
        """
        grads = np.array([self._classifier_weights[i] * self._classifiers[i].loss_gradient(x, y)
                          for i in range(self._nb_classifiers)])
        if raw:
            return grads

        return np.sum(grads, axis=0)