    def _deri_loss_func(z, x, mask, norm, lamb):
        """
        Derivative of loss function to be minimized.

        :param z: Initial guess.
        :type z: `np.ndarray`
        :param x: Original image.
        :type x: `np.ndarray`
        :param mask: A matrix that decides which points are kept.
        :type mask: `np.ndarray`
        :param norm: The norm (positive integer).
        :type norm: `int`
        :param lamb: The lambda parameter in the objective function.
        :type lamb: `float`
        :return: Derivative value.
        :rtype: `float`
        """
        # First compute the derivative of the first component of the loss function
        nor1 = np.sqrt(np.power(z - x.flatten(), 2).dot(mask.flatten()))
        if nor1 < 1e-6:
            nor1 = 1e-6
        der1 = ((z - x.flatten()) * mask.flatten()) / (nor1 * 1.0)

        # Then compute the derivative of the second component of the loss function
        z = np.reshape(z, x.shape)

        if norm == 1:
            z_d1 = np.sign(z[1:, :] - z[:-1, :])
            z_d2 = np.sign(z[:, 1:] - z[:, :-1])
        else:
            z_d1_norm = np.power(np.linalg.norm(z[1:, :] - z[:-1, :], norm, axis=1), norm - 1)
            z_d2_norm = np.power(np.linalg.norm(z[:, 1:] - z[:, :-1], norm, axis=0), norm - 1)
            z_d1_norm[z_d1_norm < 1e-6] = 1e-6
            z_d2_norm[z_d2_norm < 1e-6] = 1e-6
            z_d1_norm = np.repeat(z_d1_norm[:, np.newaxis], z.shape[1], axis=1)
            z_d2_norm = np.repeat(z_d2_norm[np.newaxis, :], z.shape[0], axis=0)
            z_d1 = norm * np.power(z[1:, :] - z[:-1, :], norm - 1) / z_d1_norm
            z_d2 = norm * np.power(z[:, 1:] - z[:, :-1], norm - 1) / z_d2_norm

        der2 = np.zeros(z.shape)
        der2[:-1, :] -= z_d1
        der2[1:, :] += z_d1
        der2[:, :-1] -= z_d2
        der2[:, 1:] += z_d2
        der2 = lamb * der2.flatten()

        # Total derivative
        return der1 + der2