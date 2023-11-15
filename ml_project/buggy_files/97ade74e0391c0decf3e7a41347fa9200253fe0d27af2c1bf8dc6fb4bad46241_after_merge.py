def cross(a, b):
    r"""Computes cross product between two vectors.

    .. math::

        \vec{w} = \vec{u} \times \vec{v} = \begin{vmatrix}
            u_{y} & y_{z} \\
            v_{y} & v_{z}
            \end{vmatrix}\vec{i} - \begin{vmatrix}
            u_{x} & u_{z} \\
            v_{x} & v_{z}
            \end{vmatrix}\vec{j} + \begin{vmatrix}
            u_{x} & u_{y} \\
            v_{x} & v_{y}
            \end{vmatrix}\vec{k}

    Parameters
    ----------

    a : ndarray
        3 Dimension vector.
    b : ndarray
        3 Dimension vector.

    Examples
    --------
    >>> i = np.array([1., 0., 0.])
    >>> j = np.array([0., 1., 0.])
    >>> cross(i, j)
    array([0., 0., 1.])

    Note
    -----
    np.cross is not supported in numba nopython mode, see
    https://github.com/numba/numba/issues/2978

    """

    return np.array(
        (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )
    )