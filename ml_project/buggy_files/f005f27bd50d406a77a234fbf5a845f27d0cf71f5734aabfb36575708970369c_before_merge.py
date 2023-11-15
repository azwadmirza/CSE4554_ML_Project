def norm(vec):
    r"""Returns the norm of a 3 dimension vector.


    .. math::

        \left \| \vec{v} \right \| = \sqrt{\sum_{i=1}^{n}v_{i}^2}

    Parameters
    ----------

    vec: ndarray
        Dimension 3 vector.


    Examples
    --------
    >>> from poliastro.core.util import norm
    >>> from astropy import units as u
    >>> vec = [1, 1, 1] * u.m
    >>> norm(vec)
    1.7320508075688772

    """

    vec = 1.0 * vec  # Cast to float
    return np.sqrt(vec.dot(vec))