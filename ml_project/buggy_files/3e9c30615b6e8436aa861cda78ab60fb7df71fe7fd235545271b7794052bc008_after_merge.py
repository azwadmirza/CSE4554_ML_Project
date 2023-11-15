def random_sphere(nb_points, nb_dims, radius, norm):
    """
    Generate randomly `m x n`-dimension points with radius `radius` and centered around 0.

    :param nb_points: Number of random data points
    :type nb_points: `int`
    :param nb_dims: Dimensionality
    :type nb_dims: `int`
    :param radius: Radius
    :type radius: `float`
    :param norm: Current support: 1, 2, np.inf
    :type norm: `int`
    :return: The generated random sphere
    :rtype: `np.ndarray`
    """
    if norm == 1:
        a = np.zeros(shape=(nb_points, nb_dims + 1))
        a[:, -1] = np.sqrt(np.random.uniform(0, radius ** 2, nb_points))

        for i in range(nb_points):
            a[i, 1:-1] = np.sort(np.random.uniform(0, a[i, -1], nb_dims - 1))

        res = (a[:, 1:] - a[:, :-1]) * np.random.choice([-1, 1], (nb_points, nb_dims))
    elif norm == 2:
        from scipy.special import gammainc

        a = np.random.randn(nb_points, nb_dims)
        s2 = np.sum(a ** 2, axis=1)
        base = gammainc(nb_dims / 2.0, s2 / 2.0) ** (1 / nb_dims) * radius / np.sqrt(s2)
        res = a * (np.tile(base, (nb_dims, 1))).T
    elif norm == np.inf:
        res = np.random.uniform(float(-radius), float(radius), (nb_points, nb_dims))
    else:
        raise NotImplementedError("Norm {} not supported".format(norm))

    return res