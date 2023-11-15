    def _minimal_perturbation(self, x, y, eps_step=0.1, eps_max=1., **kwargs):
        """Iteratively compute the minimal perturbation necessary to make the class prediction change. Stop when the
        first adversarial example was found.

        :param x: An array with the original inputs
        :type x: `np.ndarray`
        :param y:
        :type y:
        :param eps_step: The increase in the perturbation for each iteration
        :type eps_step: `float`
        :param eps_max: The maximum accepted perturbation
        :type eps_max: `float`
        :return: An array holding the adversarial examples
        :rtype: `np.ndarray`
        """
        self.set_params(**kwargs)
        adv_x = x.copy()

        # Compute perturbation with implicit batching
        for batch_id in range(int(np.ceil(adv_x.shape[0] / float(self.batch_size)))):
            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            batch = adv_x[batch_index_1:batch_index_2]
            batch_labels = y[batch_index_1:batch_index_2]

            # Get perturbation
            perturbation = self._compute_perturbation(batch, batch_labels)

            # Get current predictions
            active_indices = np.arange(len(batch))
            current_eps = eps_step
            while len(active_indices) != 0 and current_eps <= eps_max:
                # Adversarial crafting
                current_x = self._apply_perturbation(x[batch_index_1:batch_index_2], perturbation, current_eps)
                # Update
                batch[active_indices] = current_x[active_indices]
                adv_preds = self._predict(batch)
                # If targeted active check to see whether we have hit the target, otherwise head to anything but
                if self.targeted:
                    active_indices = np.where(np.argmax(batch_labels, axis=1) != np.argmax(adv_preds, axis=1))[0]
                else:
                    active_indices = np.where(np.argmax(batch_labels, axis=1) == np.argmax(adv_preds, axis=1))[0]

                current_eps += eps_step

            adv_x[batch_index_1:batch_index_2] = batch

        return adv_x