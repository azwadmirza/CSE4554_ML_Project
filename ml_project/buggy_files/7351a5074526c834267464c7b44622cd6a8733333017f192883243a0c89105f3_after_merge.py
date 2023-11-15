    def _loss_gradient(self, z, target, x_adv, x_adv_tanh, clip_min, clip_max):
        """
        Compute the gradient of the loss function.

        :param z: An array with the current logits.
        :type z: `np.ndarray`
        :param target: An array with the target class (one-hot encoded).
        :type target: `np.ndarray`
        :param x_adv: An array with the adversarial input.
        :type x_adv: `np.ndarray`
        :param x_adv_tanh: An array with the adversarial input in tanh space.
        :type x_adv_tanh: `np.ndarray`
        :param clip_min: Minimum clipping values.
        :type clip_min: `np.ndarray`
        :param clip_max: Maximum clipping values.
        :type clip_max: `np.ndarray`
        :return: An array with the gradient of the loss function.
        :type target: `np.ndarray`
        """
        if self.targeted:
            i_sub = np.argmax(target, axis=1)
            i_add = np.argmax(z * (1 - target) + (np.min(z, axis=1) - 1)[:, np.newaxis] * target, axis=1)
        else:
            i_add = np.argmax(target, axis=1)
            i_sub = np.argmax(z * (1 - target) + (np.min(z, axis=1) - 1)[:, np.newaxis] * target, axis=1)

        loss_gradient = self._class_gradient(x_adv, label=i_add, logits=True)
        loss_gradient -= self._class_gradient(x_adv, label=i_sub, logits=True)
        loss_gradient = loss_gradient.reshape(x_adv.shape)

        loss_gradient *= (clip_max - clip_min)
        loss_gradient *= (1 - np.square(np.tanh(x_adv_tanh))) / (2 * self._tanh_smoother)

        return loss_gradient