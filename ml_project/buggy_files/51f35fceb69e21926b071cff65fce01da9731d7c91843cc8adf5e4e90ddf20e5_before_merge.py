def _minimize_tnc(fun, x0, args=(), jac=None, bounds=None,
                  eps=1e-8, scale=None, offset=None, mesg_num=None,
                  maxCGit=-1, maxiter=None, eta=-1, stepmx=0, accuracy=0,
                  minfev=0, ftol=-1, xtol=-1, gtol=-1, rescale=-1, disp=False,
                  callback=None, **unknown_options):
    """
    Minimize a scalar function of one or more variables using a truncated
    Newton (TNC) algorithm.

    Options
    -------
    eps : float
        Step size used for numerical approximation of the Jacobian.
    scale : list of floats
        Scaling factors to apply to each variable. If None, the
        factors are up-low for interval bounded variables and
        1+|x] fo the others. Defaults to None.
    offset : float
        Value to subtract from each variable. If None, the
        offsets are (up+low)/2 for interval bounded variables
        and x for the others.
    disp : bool
       Set to True to print convergence messages.
    maxCGit : int
        Maximum number of hessian*vector evaluations per main
        iteration. If maxCGit == 0, the direction chosen is
        -gradient if maxCGit < 0, maxCGit is set to
        max(1,min(50,n/2)). Defaults to -1.
    maxiter : int
        Maximum number of function evaluation. If None, `maxiter` is
        set to max(100, 10*len(x0)). Defaults to None.
    eta : float
        Severity of the line search. If < 0 or > 1, set to 0.25.
        Defaults to -1.
    stepmx : float
        Maximum step for the line search. May be increased during
        call. If too small, it will be set to 10.0. Defaults to 0.
    accuracy : float
        Relative precision for finite difference calculations. If
        <= machine_precision, set to sqrt(machine_precision).
        Defaults to 0.
    minfev : float
        Minimum function value estimate. Defaults to 0.
    ftol : float
        Precision goal for the value of f in the stopping criterion.
        If ftol < 0.0, ftol is set to 0.0 defaults to -1.
    xtol : float
        Precision goal for the value of x in the stopping
        criterion (after applying x scaling factors). If xtol <
        0.0, xtol is set to sqrt(machine_precision). Defaults to
        -1.
    gtol : float
        Precision goal for the value of the projected gradient in
        the stopping criterion (after applying x scaling factors).
        If gtol < 0.0, gtol is set to 1e-2 * sqrt(accuracy).
        Setting it to 0.0 is not recommended. Defaults to -1.
    rescale : float
        Scaling factor (in log10) used to trigger f value
        rescaling. If 0, rescale at each iteration. If a large
        value, never rescale. If < 0, rescale is set to 1.3.

    """
    _check_unknown_options(unknown_options)
    epsilon = eps
    maxfun = maxiter
    fmin = minfev
    pgtol = gtol

    x0 = asfarray(x0).flatten()
    n = len(x0)

    if bounds is None:
        bounds = [(None,None)] * n
    if len(bounds) != n:
        raise ValueError('length of x0 != length of bounds')

    if mesg_num is not None:
        messages = {0:MSG_NONE, 1:MSG_ITER, 2:MSG_INFO, 3:MSG_VERS,
                    4:MSG_EXIT, 5:MSG_ALL}.get(mesg_num, MSG_ALL)
    elif disp:
        messages = MSG_ALL
    else:
        messages = MSG_NONE

    if jac is None:
        def func_and_grad(x):
            f = fun(x, *args)
            g = approx_fprime(x, fun, epsilon, *args)
            return f, g
    else:
        def func_and_grad(x):
            f = fun(x, *args)
            g = jac(x, *args)
            return f, g

    """
    low, up   : the bounds (lists of floats)
                if low is None, the lower bounds are removed.
                if up is None, the upper bounds are removed.
                low and up defaults to None
    """
    low = zeros(n)
    up = zeros(n)
    for i in range(n):
        if bounds[i] is None:
            l, u = -inf, inf
        else:
            l,u = bounds[i]
            if l is None:
                low[i] = -inf
            else:
                low[i] = l
            if u is None:
                up[i] = inf
            else:
                up[i] = u

    if scale is None:
        scale = array([])

    if offset is None:
        offset = array([])

    if maxfun is None:
        maxfun = max(100, 10*len(x0))

    rc, nf, nit, x = moduleTNC.minimize(func_and_grad, x0, low, up, scale,
                                        offset, messages, maxCGit, maxfun,
                                        eta, stepmx, accuracy, fmin, ftol,
                                        xtol, pgtol, rescale, callback)

    funv, jacv = func_and_grad(x)

    return OptimizeResult(x=x, fun=funv, jac=jacv, nfev=nf, nit=nit, status=rc,
                          message=RCSTRINGS[rc], success=(-1 < rc < 3))