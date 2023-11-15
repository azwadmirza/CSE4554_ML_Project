    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs.
        :type x: `np.ndarray`
        :param attacker: Adversarial attack name. Default is 'deepfool'. Supported names: 'carlini', 'deepfool', 'fgsm',
                'newtonfool', 'jsma', 'vat'.
        :type attacker: `str`
        :param attacker_params: Parameters specific to the adversarial attack.
        :type attacker_params: `dict`
        :param delta: desired accuracy
        :type delta: `float`
        :param max_iter: The maximum number of iterations for computing universal perturbation.
        :type max_iter: `int`
        :param eps: Attack step size (input variation)
        :type eps: `float`
        :param norm: Order of the norm. Possible values: np.inf, 1 and 2 (default is np.inf).
        :type norm: `int`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        logger.info('Computing universal perturbation based on %s attack.', self.attacker)

        self.set_params(**kwargs)

        # Init universal perturbation
        v = 0
        fooling_rate = 0.0
        nb_instances = len(x)

        # Instantiate the middle attacker and get the predicted labels
        attacker = self._get_attack(self.attacker, self.attacker_params)
        pred_y = self.classifier.predict(x, logits=False)
        pred_y_max = np.argmax(pred_y, axis=1)

        # Start to generate the adversarial examples
        nb_iter = 0
        while fooling_rate < 1. - self.delta and nb_iter < self.max_iter:
            # Go through all the examples randomly
            rnd_idx = random.sample(range(nb_instances), nb_instances)

            # Go through the data set and compute the perturbation increments sequentially
            for j, ex in enumerate(x[rnd_idx]):
                xi = ex[None, ...]

                f_xi = self.classifier.predict(xi + v, logits=True)
                fk_i_hat = np.argmax(f_xi[0])
                fk_hat = np.argmax(pred_y[rnd_idx][j])

                if fk_i_hat == fk_hat:
                    # Compute adversarial perturbation
                    adv_xi = attacker.generate(xi + v)
                    adv_f_xi = self.classifier.predict(adv_xi, logits=True)
                    adv_fk_i_hat = np.argmax(adv_f_xi[0])

                    # If the class has changed, update v
                    if fk_i_hat != adv_fk_i_hat:
                        v += adv_xi - xi

                        # Project on L_p ball
                        v = projection(v, self.eps, self.norm)
            nb_iter += 1

            # Compute the error rate
            adv_x = x + v
            adv_y = np.argmax(self.classifier.predict(adv_x, logits=False))
            fooling_rate = np.sum(pred_y_max != adv_y) / nb_instances

        self.fooling_rate = fooling_rate
        self.converged = (nb_iter < self.max_iter)
        self.v = v
        logger.info('Success rate of universal perturbation attack: %.2f%%', fooling_rate)

        return adv_x