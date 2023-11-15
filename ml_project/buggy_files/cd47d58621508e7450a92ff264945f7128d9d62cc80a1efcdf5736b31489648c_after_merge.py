    def fit(self, x, y, batch_size=128, nb_epochs=20):
        """
        Train a model adversarially. See class documentation for more information on the exact procedure.

        :param x: Training set.
        :type x: `np.ndarray`
        :param y: Labels for the training set.
        :type y: `np.ndarray`
        :param batch_size: Size of batches.
        :type batch_size: `int`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        logger.info('Performing adversarial training using %i attacks.', len(self.attacks))
        nb_batches = int(np.ceil(len(x) / batch_size))
        ind = np.arange(len(x))
        attack_id = 0

        # Precompute adversarial samples for transferred attacks
        logged = False
        self._precomputed_adv_samples = []
        for attack in self.attacks:
            if 'targeted' in attack.attack_params:
                if attack.targeted:
                    raise NotImplementedError("Adversarial training with targeted attacks is \
                                               currently not implemented")

            if attack.classifier != self.classifier:
                if not logged:
                    logger.info('Precomputing transferred adversarial samples.')
                    logged = True
                self._precomputed_adv_samples.append(attack.generate(x, y=y))
            else:
                self._precomputed_adv_samples.append(None)

        for e in range(nb_epochs):
            logger.info('Adversarial training epoch %i/%i', e, nb_epochs)

            # Shuffle the examples
            np.random.shuffle(ind)

            for batch_id in range(nb_batches):
                # Create batch data
                x_batch = x[ind[batch_id * batch_size:min((batch_id + 1) * batch_size, x.shape[0])]].copy()
                y_batch = y[ind[batch_id * batch_size:min((batch_id + 1) * batch_size, x.shape[0])]]

                nb_adv = int(np.ceil(self.ratio * x_batch.shape[0]))
                # Choose indices to replace with adversarial samples
                nb_adv = int(np.ceil(self.ratio * x_batch.shape[0]))
                attack = self.attacks[attack_id]
                if self.ratio < 1:
                    adv_ids = np.random.choice(x_batch.shape[0], size=nb_adv, replace=False)
                else:
                    adv_ids = list(range(x_batch.shape[0]))
                    np.random.shuffle(adv_ids)

                # If source and target models are the same, craft fresh adversarial samples
                if attack.classifier == self.classifier:
                    x_batch[adv_ids] = attack.generate(x_batch[adv_ids], y=y_batch[adv_ids])

                # Otherwise, use precomputed adversarial samples
                else:
                    x_adv = self._precomputed_adv_samples[attack_id]
                    x_adv = x_adv[ind[batch_id * batch_size:min((batch_id + 1) * batch_size, x.shape[0])]][adv_ids]
                    x_batch[adv_ids] = x_adv

                # Fit batch
                self.classifier.fit(x_batch, y_batch, nb_epochs=1, batch_size=x_batch.shape[0])
                attack_id = (attack_id + 1) % len(self.attacks)