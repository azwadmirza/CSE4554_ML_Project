    def generate(self, x, **kwargs):
        """Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs.
        :type x: `np.ndarray`
        :param eps: Attack step size (input variation)
        :type eps: `float`
        :param norm: Order of the norm (mimics Numpy). Possible values: np.inf, 1 or 2.
        :type norm: `int`
        :param y: The labels for the data `x`. Only provide this parameter if you'd like to use true
                  labels when crafting adversarial samples. Otherwise, model predictions are used as labels to avoid the
                  "label leaking" effect (explained in this paper: https://arxiv.org/abs/1611.01236). Default is `None`.
                  Labels should be one-hot-encoded.
        :type y: `np.ndarray`
        :param minimal: `True` if only the minimal perturbation should be computed. In that case, use `eps_step` for the
                        step size and `eps_max` for the total allowed perturbation.
        :type minimal: `bool`
        :param random_init: Whether to start at the original input or a random point within the epsilon ball
        :type random_init: `bool`
        :param batch_size: Batch size
        :type batch_size: `int`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        self.set_params(**kwargs)
        params_cpy = dict(kwargs)

        if 'y' not in params_cpy or params_cpy[str('y')] is None:
            # Throw error if attack is targeted, but no targets are provided
            if self.targeted:
                raise ValueError('Target labels `y` need to be provided for a targeted attack.')

            # Use model predictions as correct outputs
            logger.info('Using model predictions as correct labels for FGM.')
            y = get_labels_np_array(self.classifier.predict(x))
        else:
            y = params_cpy.pop(str('y'))
        y = y / np.sum(y, axis=1, keepdims=True)

        # Return adversarial examples computed with minimal perturbation if option is active
        if 'minimal' in params_cpy and params_cpy[str('minimal')]:
            logger.info('Performing minimal perturbation FGM.')
            x_adv = self._minimal_perturbation(x, y, **params_cpy)
        else:
            x_adv = self._compute(x, y, self.eps, self.random_init)

        adv_preds = np.argmax(self.classifier.predict(x_adv), axis=1)
        if self.targeted:
            rate = np.sum(adv_preds == np.argmax(y, axis=1)) / x_adv.shape[0]
        else:
            rate = np.sum(adv_preds != np.argmax(y, axis=1)) / x_adv.shape[0]
        logger.info('Success rate of FGM attack: %.2f%%', rate)

        return x_adv