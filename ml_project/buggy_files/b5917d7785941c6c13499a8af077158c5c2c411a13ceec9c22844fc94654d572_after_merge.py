def enet_path(X, y, l1_ratio=0.5, eps=1e-3, n_alphas=100, alphas=None,
              precompute='auto', Xy=None, fit_intercept=True,
              normalize=False, copy_X=True, coef_init=None,
              verbose=False, return_models=False,
              **params):
    """Compute elastic net path with coordinate descent

    The elastic net optimization function varies for mono and multi-outputs.

    For mono-output tasks it is::

        1 / (2 * n_samples) * ||y - Xw||^2_2 +
        + alpha * l1_ratio * ||w||_1
        + 0.5 * alpha * (1 - l1_ratio) * ||w||^2_2

    For multi-output tasks it is::

        (1 / (2 * n_samples)) * ||Y - XW||^Fro_2
        + alpha * l1_ratio * ||W||_21
        + 0.5 * alpha * (1 - l1_ratio) * ||W||_Fro^2

    Where::

        ||W||_21 = \sum_i \sqrt{\sum_j w_{ij}^2}

    i.e. the sum of norm of each row.

    Parameters
    ----------
    X : {array-like}, shape (n_samples, n_features)
        Training data. Pass directly as Fortran-contiguous data to avoid
        unnecessary memory duplication. If ``y`` is mono-output then ``X``
        can be sparse.

    y : ndarray, shape = (n_samples,) or (n_samples, n_outputs)
        Target values

    l1_ratio : float, optional
        float between 0 and 1 passed to elastic net (scaling between
        l1 and l2 penalties). ``l1_ratio=1`` corresponds to the Lasso

    eps : float
        Length of the path. ``eps=1e-3`` means that
        ``alpha_min / alpha_max = 1e-3``

    n_alphas : int, optional
        Number of alphas along the regularization path

    alphas : ndarray, optional
        List of alphas where to compute the models.
        If None alphas are set automatically

    precompute : True | False | 'auto' | array-like
        Whether to use a precomputed Gram matrix to speed up
        calculations. If set to ``'auto'`` let us decide. The Gram
        matrix can also be passed as argument.

    Xy : array-like, optional
        Xy = np.dot(X.T, y) that can be precomputed. It is useful
        only when the Gram matrix is precomputed.

    fit_intercept : bool
        Fit or not an intercept.
        WARNING : deprecated, will be removed in 0.16.

    normalize : boolean, optional, default False
        If ``True``, the regressors X will be normalized before regression.
        WARNING : deprecated, will be removed in 0.16.

    copy_X : boolean, optional, default True
        If ``True``, X will be copied; else, it may be overwritten.

    coef_init : array, shape (n_features, ) | None
        The initial values of the coefficients.

    verbose : bool or integer
        Amount of verbosity.

    return_models : boolean, optional, default False
        If ``True``, the function will return list of models. Setting it
        to ``False`` will change the function output returning the values
        of the alphas and the coefficients along the path. Returning the
        model list will be removed in version 0.16.

    params : kwargs
        keyword arguments passed to the coordinate descent solver.

    Returns
    -------
    models : a list of models along the regularization path
        (Is returned if ``return_models`` is set ``True`` (default).

    alphas : array, shape (n_alphas,)
        The alphas along the path where models are computed.
        (Is returned, along with ``coefs``, when ``return_models`` is set
        to ``False``)

    coefs : array, shape (n_features, n_alphas) or
            (n_outputs, n_features, n_alphas)
        Coefficients along the path.
        (Is returned, along with ``alphas``, when ``return_models`` is set
        to ``False``).

    dual_gaps : array, shape (n_alphas,)
        The dual gaps at the end of the optimization for each alpha.
        (Is returned, along with ``alphas``, when ``return_models`` is set
        to ``False``).

    Notes
    -----
    See examples/plot_lasso_coordinate_descent_path.py for an example.

    Deprecation Notice: Setting ``return_models`` to ``False`` will make
    the Lasso Path return an output in the style used by :func:`lars_path`.
    This will be become the norm as of version 0.15. Leaving ``return_models``
    set to `True` will let the function return a list of models as before.

    See also
    --------
    MultiTaskElasticNet
    MultiTaskElasticNetCV
    ElasticNet
    ElasticNetCV
    """
    if return_models:
        warnings.warn("Use enet_path(return_models=False), as it returns the"
                      " coefficients and alphas instead of just a list of"
                      " models as previously `lasso_path`/`enet_path` did."
                      " `return_models` will eventually be removed in 0.16,"
                      " after which, returning alphas and coefs"
                      " will become the norm.",
                      DeprecationWarning, stacklevel=2)

    if normalize is True:
        warnings.warn("normalize param will be removed in 0.16."
                      " Intercept fitting and feature normalization will be"
                      " done in estimators.",
                      DeprecationWarning, stacklevel=2)
    else:
        normalize = False

    if fit_intercept is True or fit_intercept is None:
        warnings.warn("fit_intercept param will be removed in 0.16."
                      " Intercept fitting and feature normalization will be"
                      " done in estimators.",
                      DeprecationWarning, stacklevel=2)

    if fit_intercept is None:
        fit_intercept = True

    X = atleast2d_or_csc(X, dtype=np.float64, order='F',
                         copy=copy_X and fit_intercept)
    n_samples, n_features = X.shape

    multi_output = False
    if y.ndim != 1:
        multi_output = True
        _, n_outputs = y.shape

    # MultiTaskElasticNet does not support sparse matrices
    if not multi_output and sparse.isspmatrix(X):
        if 'X_mean' in params:
            # As sparse matrices are not actually centered we need this
            # to be passed to the CD solver.
            X_sparse_scaling = params['X_mean'] / params['X_std']
        else:
            X_sparse_scaling = np.ones(n_features)

    X, y, X_mean, y_mean, X_std, precompute, Xy = \
        _pre_fit(X, y, Xy, precompute, normalize, fit_intercept, copy=False)
    if alphas is None:
        # No need to normalize of fit_intercept: it has been done
        # above
        alphas = _alpha_grid(X, y, Xy=Xy, l1_ratio=l1_ratio,
                             fit_intercept=False, eps=eps, n_alphas=n_alphas,
                             normalize=False, copy_X=False)
    else:
        alphas = np.sort(alphas)[::-1]  # make sure alphas are properly ordered

    n_alphas = len(alphas)
    tol = params.get('tol', 1e-4)
    positive = params.get('positive', False)
    max_iter = params.get('max_iter', 1000)
    dual_gaps = np.empty(n_alphas)
    models = []

    if not multi_output:
        coefs = np.empty((n_features, n_alphas), dtype=np.float64)
    else:
        coefs = np.empty((n_outputs, n_features, n_alphas),
                         dtype=np.float64)

    if coef_init is None:
        coef_ = np.asfortranarray(np.zeros(coefs.shape[:-1]))
    else:
        coef_ = np.asfortranarray(coef_init)

    for i, alpha in enumerate(alphas):
        l1_reg = alpha * l1_ratio * n_samples
        l2_reg = alpha * (1.0 - l1_ratio) * n_samples
        if not multi_output and sparse.isspmatrix(X):
            model = cd_fast.sparse_enet_coordinate_descent(
                coef_, l1_reg, l2_reg, X.data, X.indices,
                X.indptr, y, X_sparse_scaling,
                max_iter, tol, positive)
        elif multi_output:
            model = cd_fast.enet_coordinate_descent_multi_task(
                coef_, l1_reg, l2_reg, X, y, max_iter, tol)
        elif isinstance(precompute, np.ndarray):
            model = cd_fast.enet_coordinate_descent_gram(
                coef_, l1_reg, l2_reg, precompute, Xy, y, max_iter,
                tol, positive)
        elif precompute is False:
            model = cd_fast.enet_coordinate_descent(
                coef_, l1_reg, l2_reg, X, y, max_iter, tol, positive)
        else:
            raise ValueError("Precompute should be one of True, False, "
                            "'auto' or array-like")
        coef_, dual_gap_, eps_ = model
        coefs[..., i] = coef_
        dual_gaps[i] = dual_gap_
        if dual_gap_ > eps_:
            warnings.warn('Objective did not converge.' +
                          ' You might want' +
                          ' to increase the number of iterations',
                          ConvergenceWarning)

        if return_models:
            if not multi_output:
                model = ElasticNet(
                    alpha=alpha, l1_ratio=l1_ratio,
                    fit_intercept=fit_intercept
                    if sparse.isspmatrix(X) else False,
                    precompute=precompute)
            else:
                model = MultiTaskElasticNet(
                    alpha=alpha, l1_ratio=l1_ratio, fit_intercept=False)
            model.dual_gap_ = dual_gaps[i]
            model.coef_ = coefs[..., i]
            if (fit_intercept and not sparse.isspmatrix(X)) or multi_output:
                model.fit_intercept = True
                model._set_intercept(X_mean, y_mean, X_std)
            models.append(model)

        if verbose:
            if verbose > 2:
                print(model)
            elif verbose > 1:
                print('Path: %03i out of %03i' % (i, n_alphas))
            else:
                sys.stderr.write('.')

    if return_models:
        return models
    else:
        return alphas, coefs, dual_gaps