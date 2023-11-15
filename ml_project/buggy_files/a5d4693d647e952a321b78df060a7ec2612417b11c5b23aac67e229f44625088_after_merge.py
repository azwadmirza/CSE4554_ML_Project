def interp_rbf(data, sphere_origin, sphere_target,
               function='multiquadric', epsilon=None, smooth=0.1,
               norm="angle"):
    """Interpolate data on the sphere, using radial basis functions.

    Parameters
    ----------
    data : (N,) ndarray
        Function values on the unit sphere.
    sphere_origin : Sphere
        Positions of data values.
    sphere_target : Sphere
        M target positions for which to interpolate.

    function : {'multiquadric', 'inverse', 'gaussian'}
        Radial basis function.
    epsilon : float
        Radial basis function spread parameter. Defaults to approximate average
        distance between nodes.
    a good start
    smooth : float
        values greater than zero increase the smoothness of the
        approximation with 0 as pure interpolation. Default: 0.1
    norm : str
        A string indicating the function that returns the
        "distance" between two points.
        'angle' - The angle between two vectors
        'euclidean_norm' - The Euclidean distance

    Returns
    -------
    v : (M,) ndarray
        Interpolated values.

    See Also
    --------
    scipy.interpolate.Rbf

    """
    from scipy.interpolate import Rbf

    def angle(x1, x2):
        xx = np.arccos(np.clip((x1 * x2).sum(axis=0), -1, 1))
        return np.nan_to_num(xx)

    def euclidean_norm(x1, x2):
        return np.sqrt(((x1 - x2)**2).sum(axis=0))

    if norm == "angle":
        norm = angle
    elif norm == "euclidean_norm":
        w_s = "The Eucldian norm used for interpolation is inaccurate "
        w_s += "and will be deprecated in future versions. Please consider "
        w_s += "using the 'angle' norm instead"
        warnings.warn(w_s, DeprecationWarning)
        norm = euclidean_norm

    # Workaround for bug in older versions of SciPy that don't allow
    # specification of epsilon None:
    if epsilon is not None:
        kwargs = {'function': function,
                  'epsilon': epsilon,
                  'smooth': smooth,
                  'norm': norm}
    else:
        kwargs = {'function': function,
                  'smooth': smooth,
                  'norm': norm}

    rbfi = Rbf(sphere_origin.x, sphere_origin.y, sphere_origin.z, data,
               **kwargs)
    return rbfi(sphere_target.x, sphere_target.y, sphere_target.z)