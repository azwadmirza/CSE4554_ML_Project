    def _loss_func(self, z, x, mask, norm, lam):
        """
        Loss function to be minimized.

        :param z: Initial guess.
        :type z: `np.ndarray`
        :param x: Original image.
        :type x: `np.ndarray`
        :param mask: A matrix that decides which points are kept.
        :type mask: `np.ndarray`
        :param norm: The norm (positive integer).
        :type norm: `int`
        :param lam: The lambda parameter in the objective function.
        :type lam: `float`
        :return: Loss value.
        :rtype: `float`
        """
        res = np.sqrt(np.power(z - x.flatten(), 2).dot(mask.flatten()))
        z = np.reshape(z, x.shape)
        res += lam * np.linalg.norm(z[1:, :] - z[:-1, :], norm, axis=1).sum()
        res += lam * np.linalg.norm(z[:, 1:] - z[:, :-1], norm, axis=0).sum()

        return res