    def _saliency_map(self, x, target, search_space):
        """
        Compute the saliency map of `x`. Return the top 2 coefficients in `search_space` that maximize / minimize
        the saliency map.

        :param x: One input sample
        :type x: `np.ndarray`
        :param target: Target class for `x`
        :type target: `int`
        :param search_space: The set of valid pairs of feature indices to search
        :type search_space: `set(tuple)`
        :return: The top 2 coefficients in `search_space` that maximize / minimize the saliency map
        :rtype: `tuple`
        """
        grads = self.classifier.class_gradient(x, label=target, logits=False)
        grads = np.reshape(grads, (-1, self._nb_features))[0]

        # Remove gradients for already used features
        used_features = list(set(range(self._nb_features)) - search_space)
        coeff = 2 * int(self.theta > 0) - 1
        grads[used_features] = -np.inf * coeff

        if self.theta > 0:
            ind = np.argpartition(grads, -2)[-2:]
        else:
            ind = np.argpartition(-grads, -2)[-2:]

        return tuple(ind)