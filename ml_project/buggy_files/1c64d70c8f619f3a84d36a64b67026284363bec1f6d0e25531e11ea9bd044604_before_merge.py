    def _normalize(x):
        """
        Apply L_2 batch normalization on `x`.

        :param x: The input array to normalize.
        :type x: `np.ndarray`
        :return: The normalized version of `x`.
        :rtype: `np.ndarray`
        """
        tol = 1e-10
        dims = x.shape

        x = x.flatten()
        inverse = (np.sum(x**2) + tol) ** -.5
        x = x * inverse
        x = np.reshape(x, dims)

        return x