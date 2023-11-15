    def fit_generator(self, generator, nb_epochs=20):
        """
        Train a model adversarially using a data generator.
        See class documentation for more information on the exact procedure.

        :param generator: Data generator.
        :type generator: :class:`DataGenerator`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        logger.info('Performing adversarial training using %i attacks.', len(self.attacks))
        size = generator.size
        batch_size = generator.batch_size
        nb_batches = int(np.ceil(size / batch_size))
        ind = np.arange(generator.size)
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

                next_precomputed_adv_samples = None
                for batch_id in range(nb_batches):
                    # Create batch data
                    x_batch, y_batch = generator.get_batch()
                    x_adv_batch = attack.generate(x_batch, y=y_batch)
                    if next_precomputed_adv_samples is None:
                        next_precomputed_adv_samples = x_adv_batch
                    else:
                        next_precomputed_adv_samples = np.append(next_precomputed_adv_samples, x_adv_batch, axis=0)
                self._precomputed_adv_samples.append(next_precomputed_adv_samples)
            else:
                self._precomputed_adv_samples.append(None)

        for e in range(nb_epochs):
            logger.info('Adversarial training epoch %i/%i', e, nb_epochs)

            # Shuffle the indices of precomputed examples
            np.random.shuffle(ind)

            for batch_id in range(nb_batches):
                # Create batch data
                x_batch, y_batch = generator.get_batch()
                x_batch = x_batch.copy()

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
                    x_adv = x_adv[ind[batch_id * batch_size:min((batch_id + 1) * batch_size, size)]][adv_ids]
                    x_batch[adv_ids] = x_adv

                # Fit batch
                self.classifier.fit(x_batch, y_batch, nb_epochs=1, batch_size=x_batch.shape[0])
                attack_id = (attack_id + 1) % len(self.attacks)