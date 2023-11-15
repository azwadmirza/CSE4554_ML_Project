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
        # TODO Consider computing attack for a batch of samples at a time (no for loop)
        # Parse and save attack-specific parameters
        assert self.set_params(**kwargs)
        clip_min, clip_max = self.classifier.clip_values

        x_adv = np.copy(x)
        dims = list(x.shape[1:])
        preds = self.classifier.predict(x_adv, logits=False)
        tol = 1e-10

        for ind, val in enumerate(x_adv):
            d = np.random.randn(*dims)

            for _ in range(self.max_iter):
                d = self._normalize(d)
                preds_new = self.classifier.predict((val + d)[None, ...], logits=False)

                from scipy.stats import entropy
                kl_div1 = entropy(preds[ind], preds_new[0])

                # TODO remove for loop
                d_new = np.zeros_like(d)
                array_iter = np.nditer(d, op_flags=['readwrite'], flags=['multi_index'])
                for x in array_iter:
                    x[...] += self.finite_diff
                    preds_new = self.classifier.predict((val + d)[None, ...], logits=False)
                    kl_div2 = entropy(preds[ind], preds_new[0])
                    d_new[array_iter.multi_index] = (kl_div2 - kl_div1) / (self.finite_diff + tol)
                    x[...] -= self.finite_diff
                d = d_new

            # Apply perturbation and clip
            val = np.clip(val + self.eps * self._normalize(d), clip_min, clip_max)
            x_adv[ind] = val

        return x_adv