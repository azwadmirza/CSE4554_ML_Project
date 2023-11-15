def _lars_path_residues(X_train, y_train, X_test, y_test, Gram=None,
                        copy=True, method='lars', verbose=False,
                        fit_intercept=True, normalize=True, max_iter=500,
                        eps=np.finfo(np.float).eps):
    """Compute the residues on left-out data for a full LARS path

    Parameters
    -----------
    X_train : array, shape (n_samples, n_features)
        The data to fit the LARS on
    y_train : array, shape (n_samples)
        The target variable to fit LARS on
    X_test : array, shape (n_samples, n_features)
        The data to compute the residues on
    y_test : array, shape (n_samples)
        The target variable to compute the residues on
    Gram : None, 'auto', array, shape: (n_features, n_features), optional
        Precomputed Gram matrix (X' * X), if ``'auto'``, the Gram
        matrix is precomputed from the given X, if there are more samples
        than features
    copy : boolean, optional
        Whether X_train, X_test, y_train and y_test should be copied;
        if False, they may be overwritten.
    method : 'lar' | 'lasso'
        Specifies the returned model. Select ``'lar'`` for Least Angle
        Regression, ``'lasso'`` for the Lasso.
    verbose : integer, optional
        Sets the amount of verbosity
    fit_intercept : boolean
        whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).
    normalize : boolean, optional, default False
        If True, the regressors X will be normalized before regression.
    max_iter : integer, optional
        Maximum number of iterations to perform.
    eps : float, optional
        The machine-precision regularization in the computation of the
        Cholesky diagonal factors. Increase this for very ill-conditioned
        systems. Unlike the ``tol`` parameter in some iterative
        optimization-based algorithms, this parameter does not control
        the tolerance of the optimization.


    Returns
    --------
    alphas : array, shape (n_alphas,)
        Maximum of covariances (in absolute value) at each iteration.
        ``n_alphas`` is either ``max_iter`` or ``n_features``, whichever
        is smaller.

    active : list
        Indices of active variables at the end of the path.

    coefs : array, shape (n_features, n_alphas)
        Coefficients along the path

    residues : array, shape (n_alphas, n_samples)
        Residues of the prediction on the test data
    """
    X_train = _check_copy_and_writeable(X_train, copy)
    y_train = _check_copy_and_writeable(y_train, copy)
    X_test = _check_copy_and_writeable(X_test, copy)
    y_test = _check_copy_and_writeable(y_test, copy)

    if fit_intercept:
        X_mean = X_train.mean(axis=0)
        X_train -= X_mean
        X_test -= X_mean
        y_mean = y_train.mean(axis=0)
        y_train = as_float_array(y_train, copy=False)
        y_train -= y_mean
        y_test = as_float_array(y_test, copy=False)
        y_test -= y_mean

    if normalize:
        norms = np.sqrt(np.sum(X_train ** 2, axis=0))
        nonzeros = np.flatnonzero(norms)
        X_train[:, nonzeros] /= norms[nonzeros]

    alphas, active, coefs = lars_path(
        X_train, y_train, Gram=Gram, copy_X=False, copy_Gram=False,
        method=method, verbose=max(0, verbose - 1), max_iter=max_iter, eps=eps)
    if normalize:
        coefs[nonzeros] /= norms[nonzeros][:, np.newaxis]
    residues = np.dot(X_test, coefs) - y_test[:, np.newaxis]
    return alphas, active, coefs, residues.T