    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs to be attacked.
        :type x: `np.ndarray`
        :param y: Target values if the attack is targeted
        :type y: `np.ndarray`
        :param theta: Perturbation introduced to each modified feature per step (can be positive or negative)
        :type theta: `float`
        :param gamma: Maximum percentage of perturbed features (between 0 and 1)
        :type gamma: `float`
        :param batch_size: Batch size
        :type batch_size: `int`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        # Parse and save attack-specific parameters
        self.set_params(**kwargs)
        clip_min, clip_max = self.classifier.clip_values

        # Initialize variables
        dims = list(x.shape[1:])
        self._nb_features = np.product(dims)
        x_adv = np.reshape(np.copy(x), (-1, self._nb_features))
        preds = np.argmax(self._predict(x), axis=1)

        # Determine target classes for attack
        if 'y' not in kwargs or kwargs[str('y')] is None:
            # Randomly choose target from the incorrect classes for each sample
            from art.utils import random_targets
            targets = np.argmax(random_targets(preds, self.classifier.nb_classes), axis=1)
        else:
            targets = np.argmax(kwargs[str('y')], axis=1)

        # Compute perturbation with implicit batching
        for batch_id in range(int(np.ceil(x_adv.shape[0] / float(self.batch_size)))):
            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            batch = x_adv[batch_index_1:batch_index_2]

            # Main algorithm for each batch
            # Initialize the search space; optimize to remove features that can't be changed
            search_space = np.zeros_like(batch)
            if self.theta > 0:
                search_space[batch < clip_max] = 1
            else:
                search_space[batch > clip_min] = 1

            # Get current predictions
            current_pred = preds[batch_index_1:batch_index_2]
            target = targets[batch_index_1:batch_index_2]
            active_indices = np.where(current_pred != target)[0]
            all_feat = np.zeros_like(batch)

            while len(active_indices) != 0:
                # Compute saliency map
                feat_ind = self._saliency_map(np.reshape(batch, [batch.shape[0]] + dims)[active_indices],
                                              target[active_indices], search_space[active_indices])

                # Update used features
                all_feat[active_indices][np.arange(len(active_indices)), feat_ind[:, 0]] = 1
                all_feat[active_indices][np.arange(len(active_indices)), feat_ind[:, 1]] = 1

                # Prepare update depending of theta
                if self.theta > 0:
                    clip_func, clip_value = np.minimum, clip_max
                else:
                    clip_func, clip_value = np.maximum, clip_min

                # Update adversarial examples
                tmp_batch = batch[active_indices]
                tmp_batch[np.arange(len(active_indices)), feat_ind[:, 0]] = clip_func(clip_value,
                    tmp_batch[np.arange(len(active_indices)), feat_ind[:, 0]] + self.theta)
                tmp_batch[np.arange(len(active_indices)), feat_ind[:, 1]] = clip_func(clip_value,
                    tmp_batch[np.arange(len(active_indices)), feat_ind[:, 1]] + self.theta)
                batch[active_indices] = tmp_batch

                # Remove indices from search space if max/min values were reached
                search_space[batch == clip_value] = 0

                # Recompute model prediction
                current_pred = np.argmax(self._predict(np.reshape(batch, [batch.shape[0]] + dims)), axis=1)

                # Update active_indices
                active_indices = np.where((current_pred != target) *
                                          (np.sum(all_feat, axis=1) / self._nb_features <= self.gamma) *
                                          (np.sum(search_space, axis=1) > 0))[0]

            x_adv[batch_index_1:batch_index_2] = batch

        x_adv = np.reshape(x_adv, x.shape)
        preds = np.argmax(self._predict(x), axis=1)
        preds_adv = np.argmax(self._predict(x_adv), axis=1)
        logger.info('Success rate of JSMA attack: %.2f%%', (np.sum(preds != preds_adv) / x.shape[0]))

        return x_adv