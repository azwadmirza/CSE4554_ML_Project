    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs to be attacked.
        :type x: `np.ndarray`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param epsilon: Overshoot parameter.
        :type epsilon: `float`
        :param nb_grads: The number of class gradients (top nb_grads w.r.t. prediction) to compute. This way only the
                         most likely classes are considered, speeding up the computation.
        :type nb_grads: `int`
        :param batch_size: Batch size
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        self.set_params(**kwargs)
        clip_min, clip_max = self.classifier.clip_values
        x_adv = x.copy()
        preds = self._predict(x, logits=True)

        # Determine the class labels for which to compute the gradients
        use_grads_subset = self.nb_grads < self.classifier.nb_classes
        if use_grads_subset:
            # TODO compute set of unique labels per batch
            grad_labels = np.argsort(-preds, axis=1)[:, :self.nb_grads]
            labels_set = np.unique(grad_labels)
        else:
            labels_set = np.arange(self.classifier.nb_classes)
        sorter = np.arange(len(labels_set))

        # Pick a small scalar to avoid division by 0
        tol = 10e-8

        # Compute perturbation with implicit batching
        for batch_id in range(int(np.ceil(x_adv.shape[0] / float(self.batch_size)))):
            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            batch = x_adv[batch_index_1:batch_index_2]

            # Get predictions and gradients for batch
            f = preds[batch_index_1:batch_index_2]
            fk_hat = np.argmax(f, axis=1)
            if use_grads_subset:
                # Compute gradients only for top predicted classes
                grd = np.array([self._class_gradient(batch, logits=True, label=_) for _ in labels_set])
                grd = np.squeeze(np.swapaxes(grd, 0, 2), axis=0)
            else:
                # Compute gradients for all classes
                grd = self._class_gradient(batch, logits=True)

            # Get current predictions
            active_indices = np.arange(len(batch))
            current_step = 0
            while len(active_indices) != 0 and current_step < self.max_iter:
                # Compute difference in predictions and gradients only for selected top predictions
                labels_indices = sorter[np.searchsorted(labels_set, fk_hat, sorter=sorter)]
                grad_diff = grd - grd[np.arange(len(grd)), labels_indices][:, None]
                f_diff = f[:, labels_set] - f[np.arange(len(f)), labels_indices][:, None]

                # Choose coordinate and compute perturbation
                norm = np.linalg.norm(grad_diff.reshape(len(grad_diff), len(labels_set), -1), axis=2) + tol
                value = np.abs(f_diff) / norm
                value[np.arange(len(value)), labels_indices] = np.inf
                l = np.argmin(value, axis=1)
                r = (abs(f_diff[np.arange(len(f_diff)), l]) / (pow(np.linalg.norm(grad_diff[np.arange(len(
                    grad_diff)), l].reshape(len(grad_diff), -1), axis=1), 2) + tol))[:, None, None, None] * \
                    grad_diff[np.arange(len(grad_diff)), l]

                # Add perturbation and clip result
                batch[active_indices] = np.clip(batch[active_indices] + r[active_indices], clip_min, clip_max)

                # Recompute prediction for new x
                f = self._predict(batch, logits=True)
                fk_i_hat = np.argmax(f, axis=1)

                # Recompute gradients for new x
                if use_grads_subset:
                    # Compute gradients only for (originally) top predicted classes
                    grd = np.array([self._class_gradient(batch, logits=True, label=_) for _ in labels_set])
                    grd = np.squeeze(np.swapaxes(grd, 0, 2), axis=0)
                else:
                    # Compute gradients for all classes
                    grd = self._class_gradient(batch, logits=True)

                # Stop if misclassification has been achieved
                active_indices = np.where(fk_i_hat != fk_hat)[0]
                current_step += 1

                current_step += 1

            # Apply overshoot parameter
            x_adv[batch_index_1:batch_index_2] = np.clip(x_adv[batch_index_1:batch_index_2] + (
                1 + self.epsilon) * (batch - x_adv[batch_index_1:batch_index_2]), clip_min, clip_max)

        preds = np.argmax(preds, axis=1)
        preds_adv = np.argmax(self._predict(x_adv), axis=1)
        logger.info('Success rate of DeepFool attack: %.2f%%', (np.sum(preds != preds_adv) / x.shape[0]))

        return x_adv