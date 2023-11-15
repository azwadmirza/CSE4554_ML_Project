    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in a Numpy array.

        :param x: An array with the original inputs to be attacked.
        :type x: `np.ndarray`
        :param kwargs: Attack-specific parameters used by child classes.
        :type kwargs: `dict`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        self.set_params(**kwargs)
        x_adv = x.copy()

        # Initialize variables
        clip_min, clip_max = self.classifier.clip_values
        y_pred = self._predict(x, logits=False)
        pred_class = np.argmax(y_pred, axis=1)

        # Compute perturbation with implicit batching
        for batch_id in range(int(np.ceil(x_adv.shape[0] / float(self.batch_size)))):
            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            batch = x_adv[batch_index_1:batch_index_2]

            # Main algorithm for each batch
            norm_batch = np.linalg.norm(np.reshape(batch, (batch.shape[0], -1)), axis=1)
            l = pred_class[batch_index_1:batch_index_2]
            l_b = to_categorical(l, self.classifier.nb_classes).astype(bool)

            # Main loop of the algorithm
            for _ in range(self.max_iter):
                # Compute score
                score = self._predict(batch, logits=False)[l_b]

                # Compute the gradients and norm
                grads = self._class_gradient(batch, label=l, logits=False)
                grads = np.squeeze(grads, axis=1)
                norm_grad = np.linalg.norm(np.reshape(grads, (batch.shape[0], -1)), axis=1)

                # Theta
                theta = self._compute_theta(norm_batch, score, norm_grad)

                # Pertubation
                di_batch = self._compute_pert(theta, grads, norm_grad)

                # Update xi and pertubation
                batch += di_batch

            # Apply clip
            x_adv[batch_index_1:batch_index_2] = np.clip(batch, clip_min, clip_max)

        preds = np.argmax(self._predict(x), axis=1)
        preds_adv = np.argmax(self._predict(x_adv), axis=1)
        logger.info('Success rate of NewtonFool attack: %.2f%%', (np.sum(preds != preds_adv) / x.shape[0]))

        return x_adv