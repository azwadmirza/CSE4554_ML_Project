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
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        # Parse and save attack-specific parameters
        self.set_params(**kwargs)
        clip_min, clip_max = self.classifier.clip_values

        # Initialize variables
        dims = [1] + list(x.shape[1:])
        self._nb_features = np.product(dims)
        x_adv = np.reshape(np.copy(x), (-1, self._nb_features))
        preds = np.argmax(self.classifier.predict(x), axis=1)

        # Determine target classes for attack
        if 'y' not in kwargs or kwargs[str('y')] is None:
            # Randomly choose target from the incorrect classes for each sample
            from art.utils import random_targets
            targets = np.argmax(random_targets(preds, self.classifier.nb_classes), axis=1)
        else:
            targets = np.argmax(kwargs[str('y')], axis=1)

        # Generate the adversarial samples
        for ind, val in enumerate(x_adv):
            # Initialize the search space; optimize to remove features that can't be changed
            if self.theta > 0:
                search_space = {i for i in range(self._nb_features) if val[i] < clip_max}
            else:
                search_space = {i for i in range(self._nb_features) if val[i] > clip_min}

            current_pred = preds[ind]
            target = targets[ind]
            all_feat = set()

            while current_pred != target and len(all_feat) / self._nb_features <= self.gamma and bool(search_space):
                # Compute saliency map
                feat1, feat2 = self._saliency_map(np.reshape(val, dims), target, search_space)

                # Move on to next examples if there are no more features to change
                if feat1 == feat2 == 0:
                    break

                all_feat = all_feat.union(set([feat1, feat2]))

                # Prepare update depending of theta
                if self.theta > 0:
                    clip_func, clip_value = np.minimum, clip_max
                else:
                    clip_func, clip_value = np.maximum, clip_min

                # Update adversarial example
                for feature_ind in [feat1, feat2]:
                    val[feature_ind] = clip_func(clip_value, val[feature_ind] + self.theta)

                    # Remove indices from search space if max/min values were reached
                    if val[feature_ind] == clip_value:
                        search_space.discard(feature_ind)

                # Recompute model prediction
                current_pred = np.argmax(self.classifier.predict(np.reshape(val, dims)), axis=1)

        x_adv = np.reshape(x_adv, x.shape)
        preds = np.argmax(self.classifier.predict(x), axis=1)
        preds_adv = np.argmax(self.classifier.predict(x_adv), axis=1)
        logger.info('Success rate of JSMA attack: %.2f%%', (np.sum(preds != preds_adv) / x.shape[0]))

        return x_adv