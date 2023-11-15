    def _saliency_map(self, x, target, search_space):
        """
        Compute the saliency map of `x`. Return the top 2 coefficients in `search_space` that maximize / minimize
        the saliency map.

        :param x: A batch of input samples
        :type x: `np.ndarray`
        :param target: Target class for `x`
        :type target: `np.ndarray`
        :param search_space: The set of valid pairs of feature indices to search
        :type search_space: `np.ndarray`
        :return: The top 2 coefficients in `search_space` that maximize / minimize the saliency map
        :rtype: `np.ndarray`
        """
        grads = self._class_gradient(x, label=target, logits=False)
        grads = np.reshape(grads, (-1, self._nb_features))

        # Remove gradients for already used features
        used_features = 1 - search_space
        coeff = 2 * int(self.theta > 0) - 1
        grads[used_features == 1] = -np.inf * coeff

        if self.theta > 0:
            ind = np.argpartition(grads, -2, axis=1)[:, -2:]
        else:
            ind = np.argpartition(-grads, -2, axis=1)[:, -2:]

        return ind