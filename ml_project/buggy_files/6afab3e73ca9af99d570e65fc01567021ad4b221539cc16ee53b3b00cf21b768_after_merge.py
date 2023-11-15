    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs to be attacked.
        :type x: `np.ndarray`
        :param eps: Attack step (max input variation).
        :type eps: `float`
        :param finite_diff: The finite difference parameter.
        :type finite_diff: `float`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :return: An array holding the adversarial examples.
        :rtype: `np.ndarray`
        """
        # Parse and save attack-specific parameters
        assert self.set_params(**kwargs)
        clip_min, clip_max = self.classifier.clip_values
        x_adv = np.copy(x)
        dims = list(x.shape[1:])
        preds = self._predict(x_adv, logits=False)

        # Pick a small scalar to avoid division by 0
        tol = 1e-10

        # Compute perturbation with implicit batching
        for batch_id in range(int(np.ceil(x_adv.shape[0] / float(self.batch_size)))):
            batch_index_1, batch_index_2 = batch_id * self.batch_size, (batch_id + 1) * self.batch_size
            batch = x_adv[batch_index_1:batch_index_2]

            # Main algorithm for each batch
            d = np.random.randn(*batch.shape)

            # Main loop of the algorithm
            for _ in range(self.max_iter):
                d = self._normalize(d)
                preds_new = self._predict(batch + d, logits=False)

                from scipy.stats import entropy
                kl_div1 = entropy(np.transpose(preds[batch_index_1:batch_index_2]), np.transpose(preds_new))

                d_new = np.zeros_like(d)
                for w in range(d.shape[1]):
                    for h in range(d.shape[2]):
                        for c in range(d.shape[3]):
                            d[:, w, h, c] += self.finite_diff
                            preds_new = self._predict(batch + d, logits=False)
                            kl_div2 = entropy(np.transpose(preds[batch_index_1:batch_index_2]), np.transpose(preds_new))
                            d_new[:, w, h, c] = (kl_div2 - kl_div1) / (self.finite_diff + tol)
                            d[:, w, h, c] -= self.finite_diff
                d = d_new

            # Apply perturbation and clip
            x_adv[batch_index_1:batch_index_2] = np.clip(batch + self.eps * self._normalize(d), clip_min, clip_max)

        return x_adv