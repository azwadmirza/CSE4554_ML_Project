    def _minimize(self, x, mask):
        """
        Minimize the total variance objective function.

        :param x: Original image.
        :type x: `np.ndarray`
        :param mask: A matrix that decides which points are kept.
        :type mask: `np.ndarray`
        :return: A new image.
        :rtype: `np.ndarray`
        """
        z = x.copy()

        for i in range(x.shape[2]):
            res = minimize(self._loss_func, z[:, :, i].flatten(), (x[:, :, i], mask[:, :, i], self.norm, self.lam),
                           method=self.solver, jac=self._deri_loss_func, options={'maxiter': self.maxiter})
            z[:, :, i] = np.reshape(res.x, z[:, :, i].shape)

        return z