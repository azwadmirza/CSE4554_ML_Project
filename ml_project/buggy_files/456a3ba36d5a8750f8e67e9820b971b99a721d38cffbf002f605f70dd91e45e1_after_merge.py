    def _loss(self, x_adv, target):
        """
        Compute the objective function value.

        :param x_adv: An array with the adversarial input.
        :type x_adv: `np.ndarray`
        :param target: An array with the target class (one-hot encoded).
        :type target: `np.ndarray`
        :return: A tuple holding the current logits and overall loss.
        :rtype: `(float, float)`
        """
        z = self._predict(np.array(x_adv, dtype=NUMPY_DTYPE), logits=True)
        z_target = np.sum(z * target, axis=1)
        z_other = np.max(z * (1 - target) + (np.min(z, axis=1) - 1)[:, np.newaxis] * target, axis=1)

        if self.targeted:
            # if targeted, optimize for making the target class most likely
            loss = np.maximum(z_other - z_target + self.confidence, np.zeros(x_adv.shape[0]))
        else:
            # if untargeted, optimize for making any other class most likely
            loss = np.maximum(z_target - z_other + self.confidence, np.zeros(x_adv.shape[0]))

        return z, loss