    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs.
        :type x: `np.ndarray`
        :param norm: Order of the norm. Possible values: np.inf, 1 or 2.
        :type norm: `int`
        :param eps: Maximum perturbation that the attacker can introduce.
        :type eps: `float`
        :param eps_step: Attack step size (input variation) at each iteration.
        :type eps_step: `float`
        :param y: The labels for the data `x`. Only provide this parameter if you'd like to use true
                  labels when crafting adversarial samples. Otherwise, model predictions are used as labels to avoid the
                  "label leaking" effect (explained in this paper: https://arxiv.org/abs/1611.01236). Default is `None`.
                  Labels should be one-hot-encoded.
        :type y: `np.ndarray`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        from art.utils import projection

        self.set_params(**kwargs)

        adv_x = x.copy()
        if 'y' not in kwargs or kwargs[str('y')] is None:
            # Throw error if attack is targeted, but no targets are provided
            if self.targeted:
                raise ValueError('Target labels `y` need to be provided for a targeted attack.')

            # Use model predictions as correct outputs
            targets = get_labels_np_array(self.classifier.predict(x))
        else:
            targets = kwargs['y']
        target_labels = np.argmax(targets, axis=1)

        for i in range(self.max_iter):
            # Adversarial crafting
            adv_x = self._compute(adv_x, targets, self.eps_step, self.random_init and i == 0)

            if self._project:
                noise = projection(adv_x - x, self.eps, self.norm)
                adv_x = x + noise

        adv_preds = np.argmax(self.classifier.predict(adv_x), axis=1)
        if self.targeted:
            rate = np.sum(adv_preds == target_labels) / adv_x.shape[0]
        else:
            rate = np.sum(adv_preds != target_labels) / adv_x.shape[0]
        logger.info('Success rate of BIM attack: %.2f%%', rate)

        return adv_x