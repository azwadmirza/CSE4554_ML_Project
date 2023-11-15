    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs to be attacked.
        :type x: `np.ndarray`
        :param y: If `self.targeted` is true, then `y_val` represents the target labels. Otherwise, the targets are
                the original class labels.
        :type y: `np.ndarray`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        x_adv = x.astype(NUMPY_DTYPE)
        (clip_min, clip_max) = self.classifier.clip_values

        # Parse and save attack-specific parameters
        params_cpy = dict(kwargs)
        y = params_cpy.pop(str('y'), None)
        self.set_params(**params_cpy)

        # Assert that, if attack is targeted, y_val is provided:
        if self.targeted and y is None:
            raise ValueError('Target labels `y` need to be provided for a targeted attack.')

        # No labels provided, use model prediction as correct class
        if y is None:
            y = get_labels_np_array(self._predict(x, logits=False))

        # Compute perturbation with implicit batching
        nb_batches = int(np.ceil(x_adv.shape[0] / float(self.batch_size)))
        for batch_id in range(nb_batches):
            logger.debug('Processing batch %i out of %i', batch_id, nb_batches)

            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            x_batch = x_adv[batch_index_1:batch_index_2]
            y_batch = y[batch_index_1:batch_index_2]

            # The optimization is performed in tanh space to keep the
            # adversarial images bounded from clip_min and clip_max.
            x_batch_tanh = self._original_to_tanh(x_batch, clip_min, clip_max)

            # Initialize binary search:
            c = self.initial_const * np.ones(x_batch.shape[0])
            c_lower_bound = np.zeros(x_batch.shape[0])
            c_double = (np.ones(x_batch.shape[0]) > 0)

            # Initialize placeholders for best l2 distance and attack found so far
            best_l2dist = np.inf * np.ones(x_batch.shape[0])
            best_x_adv_batch = x_batch.copy()

            for bss in range(self.binary_search_steps):
                logger.debug('Binary search step %i out of %i (c_mean==%f)', bss, self.binary_search_steps, np.mean(c))
                nb_active = int(np.sum(c < self._c_upper_bound))
                logger.debug('Number of samples with c < _c_upper_bound: %i out of %i', nb_active, x_batch.shape[0])
                if nb_active == 0:
                    break
                lr = self.learning_rate * np.ones(x_batch.shape[0])

                # Initialize perturbation in tanh space:
                x_adv_batch = x_batch.copy()
                x_adv_batch_tanh = x_batch_tanh.copy()

                z, l2dist, loss = self._loss(x_batch, x_adv_batch, y_batch, c)
                attack_success = (loss - l2dist <= 0)
                overall_attack_success = attack_success

                for it in range(self.max_iter):
                    logger.debug('Iteration step %i out of %i', it, self.max_iter)
                    logger.debug('Average Loss: %f', np.mean(loss))
                    logger.debug('Average L2Dist: %f', np.mean(l2dist))
                    logger.debug('Average Margin Loss: %f', np.mean(loss-l2dist))
                    logger.debug('Current number of succeeded attacks: %i out of %i', int(np.sum(attack_success)),
                                 len(attack_success))

                    improved_adv = attack_success & (l2dist < best_l2dist)
                    logger.debug('Number of improved L2 distances: %i', int(np.sum(improved_adv)))
                    if np.sum(improved_adv) > 0:
                        best_l2dist[improved_adv] = l2dist[improved_adv]
                        best_x_adv_batch[improved_adv] = x_adv_batch[improved_adv]

                    active = (c < self._c_upper_bound) & (lr > 0)
                    nb_active = int(np.sum(active))
                    logger.debug('Number of samples with c < _c_upper_bound and lr > 0: %i out of %i',
                                 nb_active, x_batch.shape[0])
                    if nb_active == 0:
                        break

                    # compute gradient:
                    logger.debug('Compute loss gradient')
                    perturbation_tanh = -self._loss_gradient(z[active], y_batch[active], x_batch[active],
                                                             x_adv_batch[active], x_adv_batch_tanh[active],
                                                             c[active], clip_min, clip_max)

                    # perform line search to optimize perturbation
                    # first, halve the learning rate until perturbation actually decreases the loss:
                    prev_loss = loss.copy()
                    best_loss = loss.copy()
                    best_lr = np.zeros(x_batch.shape[0])
                    halving = np.zeros(x_batch.shape[0])

                    for h in range(self.max_halving):
                        logger.debug('Perform halving iteration %i out of %i', h, self.max_halving)
                        do_halving = (loss[active] >= prev_loss[active])
                        logger.debug('Halving to be performed on %i samples', int(np.sum(do_halving)))
                        if np.sum(do_halving) == 0:
                            break
                        active_and_do_halving = active.copy()
                        active_and_do_halving[active] = do_halving

                        lr_mult = lr[active_and_do_halving]
                        for _ in range(len(x.shape)-1):
                            lr_mult = lr_mult[:, np.newaxis]

                        new_x_adv_batch_tanh = x_adv_batch_tanh[active_and_do_halving] + \
                            lr_mult * perturbation_tanh[do_halving]
                        new_x_adv_batch = self._tanh_to_original(new_x_adv_batch_tanh, clip_min, clip_max)
                        _, l2dist[active_and_do_halving], loss[active_and_do_halving] = self._loss(
                            x_batch[active_and_do_halving], new_x_adv_batch, y_batch[active_and_do_halving],
                            c[active_and_do_halving])

                        logger.debug('New Average Loss: %f', np.mean(loss))
                        logger.debug('New Average L2Dist: %f', np.mean(l2dist))
                        logger.debug('New Average Margin Loss: %f', np.mean(loss-l2dist))

                        best_lr[loss < best_loss] = lr[loss < best_loss]
                        best_loss[loss < best_loss] = loss[loss < best_loss]
                        lr[active_and_do_halving] /= 2
                        halving[active_and_do_halving] += 1
                    lr[active] *= 2

                    # if no halving was actually required, double the learning rate as long as this
                    # decreases the loss:
                    for d in range(self.max_doubling):
                        logger.debug('Perform doubling iteration %i out of %i', d, self.max_doubling)
                        do_doubling = (halving[active] == 1) & (loss[active] <= best_loss[active])
                        logger.debug('Doubling to be performed on %i samples', int(np.sum(do_doubling)))
                        if np.sum(do_doubling) == 0:
                            break
                        active_and_do_doubling = active.copy()
                        active_and_do_doubling[active] = do_doubling
                        lr[active_and_do_doubling] *= 2

                        lr_mult = lr[active_and_do_doubling]
                        for _ in range(len(x.shape)-1):
                            lr_mult = lr_mult[:, np.newaxis]

                        new_x_adv_batch_tanh = x_adv_batch_tanh[active_and_do_doubling] + \
                            lr_mult * perturbation_tanh[do_doubling]
                        new_x_adv_batch = self._tanh_to_original(new_x_adv_batch_tanh, clip_min, clip_max)
                        _, l2dist[active_and_do_doubling], loss[active_and_do_doubling] = self._loss(
                            x_batch[active_and_do_doubling], new_x_adv_batch, y_batch[active_and_do_doubling],
                            c[active_and_do_doubling])
                        logger.debug('New Average Loss: %f', np.mean(loss))
                        logger.debug('New Average L2Dist: %f', np.mean(l2dist))
                        logger.debug('New Average Margin Loss: %f', np.mean(loss-l2dist))
                        best_lr[loss < best_loss] = lr[loss < best_loss]
                        best_loss[loss < best_loss] = loss[loss < best_loss]

                    lr[halving == 1] /= 2

                    update_adv = (best_lr[active] > 0)
                    logger.debug('Number of adversarial samples to be finally updated: %i', int(np.sum(update_adv)))

                    if np.sum(update_adv) > 0:
                        active_and_update_adv = active.copy()
                        active_and_update_adv[active] = update_adv
                        best_lr_mult = best_lr[active_and_update_adv]
                        for _ in range(len(x.shape) - 1):
                            best_lr_mult = best_lr_mult[:, np.newaxis]

                        x_adv_batch_tanh[active_and_update_adv] = x_adv_batch_tanh[active_and_update_adv] + \
                            best_lr_mult * perturbation_tanh[update_adv]
                        x_adv_batch[active_and_update_adv] = \
                            self._tanh_to_original(x_adv_batch_tanh[active_and_update_adv], clip_min, clip_max)
                        z[active_and_update_adv], l2dist[active_and_update_adv], loss[active_and_update_adv] = \
                            self._loss(x_batch[active_and_update_adv], x_adv_batch[active_and_update_adv],
                                       y_batch[active_and_update_adv], c[active_and_update_adv])
                        attack_success = (loss - l2dist <= 0)
                        overall_attack_success = overall_attack_success | attack_success

                # Update depending on attack success:
                improved_adv = attack_success & (l2dist < best_l2dist)
                logger.debug('Number of improved L2 distances: %i', int(np.sum(improved_adv)))

                if np.sum(improved_adv) > 0:
                    best_l2dist[improved_adv] = l2dist[improved_adv]
                    best_x_adv_batch[improved_adv] = x_adv_batch[improved_adv]

                c_double[overall_attack_success] = False
                c[overall_attack_success] = (c_lower_bound + c)[overall_attack_success] / 2

                c_old = c
                c[~overall_attack_success & c_double] *= 2
                c[~overall_attack_success & ~c_double] += (c - c_lower_bound)[~overall_attack_success & ~c_double] / 2
                c_lower_bound[~overall_attack_success] = c_old[~overall_attack_success]

            x_adv[batch_index_1:batch_index_2] = best_x_adv_batch

        adv_preds = np.argmax(self._predict(x_adv), axis=1)
        if self.targeted:
            rate = np.sum(adv_preds == np.argmax(y, axis=1)) / x_adv.shape[0]
        else:
            preds = np.argmax(self._predict(x), axis=1)
            rate = np.sum(adv_preds != preds) / x_adv.shape[0]
        logger.info('Success rate of C&W attack: %.2f%%', 100*rate)

        return x_adv