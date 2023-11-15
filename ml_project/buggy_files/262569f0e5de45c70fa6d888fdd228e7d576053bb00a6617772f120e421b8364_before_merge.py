def check_diagrams(X, copy=False):
    """Input validation for collections of persistence diagrams.

    Basic type and sanity checks are run on the input collection and the
    array is converted to float type before returning. In particular,
    the input is checked to be an ndarray of shape ``(n_samples, n_points,
    3)``.

    Parameters
    ----------
    X : object
        Input object to check/convert.

    copy : bool, optional, default: ``False``
        Whether a forced copy should be triggered.

    Returns
    -------
    X_validated : ndarray of shape (n_samples, n_points, 3)
        The converted and validated array of persistence diagrams.

    """
    X_array = np.asarray(X)
    if X_array.ndim == 0:
        raise ValueError(
            f"Expected 3D array, got scalar array instead:\narray={X_array}.")
    if X_array.ndim != 3:
        raise ValueError(
            f"Input should be a 3D ndarray, the shape is {X_array.shape}.")
    if X_array.shape[2] != 3:
        raise ValueError(
            f"Input should be a 3D ndarray with a 3rd dimension of 3 "
            f"components, but there are {X_array.shape[2]} components.")

    X_array = X_array.astype(float, copy=False)
    homology_dimensions = sorted(list(set(X_array[0, :, 2])))
    for dim in homology_dimensions:
        if dim == np.inf:
            if len(homology_dimensions) != 1:
                raise ValueError(
                    f"np.inf is a valid homology dimension for a stacked "
                    f"diagram but it should be the only one: "
                    f"homology_dimensions = {homology_dimensions}.")
        else:
            if dim != int(dim):
                raise ValueError(
                    f"All homology dimensions should be integer valued: "
                    f"{dim} can't be cast to an int of the same value.")
            if dim != np.abs(dim):
                raise ValueError(
                    f"All homology dimensions should be integer valued: "
                    f"{dim} can't be cast to an int of the same value.")

    n_points_above_diag = np.sum(X_array[:, :, 1] >= X_array[:, :, 0])
    n_points_global = X_array.shape[0] * X_array.shape[1]
    if n_points_above_diag != n_points_global:
        raise ValueError(
            f"All points of all persistence diagrams should be above the "
            f"diagonal, i.e. X[:,:,1] >= X[:,:,0]. "
            f"{n_points_global - n_points_above_diag} points are under the "
            f"diagonal.")
    if copy:
        X_array = np.copy(X_array)

    return X_array