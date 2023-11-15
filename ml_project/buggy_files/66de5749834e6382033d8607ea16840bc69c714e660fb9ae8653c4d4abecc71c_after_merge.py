def bisplrep(x, y, z, w=None, xb=None, xe=None, yb=None, ye=None,
             kx=3, ky=3, task=0, s=None, eps=1e-16, tx=None, ty=None,
             full_output=0, nxest=None, nyest=None, quiet=1, cache=None):
    """
    Find a bivariate B-spline representation of a surface.

    Given a set of data points (x[i], y[i], z[i]) representing a surface
    z=f(x,y), compute a B-spline representation of the surface. Based on
    the routine SURFIT from FITPACK.

    Parameters
    ----------
    x, y, z : ndarray
        Rank-1 arrays of data points.
    w : ndarray, optional
        Rank-1 array of weights. By default ``w=np.ones(len(x))``.
    xb, xe : float, optional
        End points of approximation interval in `x`.
        By default ``xb = x.min(), xe=x.max()``.
    yb, ye : float, optional
        End points of approximation interval in `y`.
        By default ``yb=y.min(), ye = y.max()``.
    kx, ky : int, optional
        The degrees of the spline (1 <= kx, ky <= 5).
        Third order (kx=ky=3) is recommended.
    task : int, optional
        If task=0, find knots in x and y and coefficients for a given
        smoothing factor, s.
        If task=1, find knots and coefficients for another value of the
        smoothing factor, s.  bisplrep must have been previously called
        with task=0 or task=1.
        If task=-1, find coefficients for a given set of knots tx, ty.
    s : float, optional
        A non-negative smoothing factor.  If weights correspond
        to the inverse of the standard-deviation of the errors in z,
        then a good s-value should be found in the range
        ``(m-sqrt(2*m),m+sqrt(2*m))`` where m=len(x).
    eps : float, optional
        A threshold for determining the effective rank of an
        over-determined linear system of equations (0 < eps < 1).
        `eps` is not likely to need changing.
    tx, ty : ndarray, optional
        Rank-1 arrays of the knots of the spline for task=-1
    full_output : int, optional
        Non-zero to return optional outputs.
    nxest, nyest : int, optional
        Over-estimates of the total number of knots. If None then
        ``nxest = max(kx+sqrt(m/2),2*kx+3)``,
        ``nyest = max(ky+sqrt(m/2),2*ky+3)``.
    quiet : int, optional
        Non-zero to suppress printing of messages.
        This parameter is deprecated; use standard Python warning filters
        instead.
    cache : dict, optional
        Stores the results of a previous call of bisplrep for the same data, to
        be used when task==1 after a previous call with task==0 or task==-1.

    Returns
    -------
    tck : array_like
        A list [tx, ty, c, kx, ky] containing the knots (tx, ty) and
        coefficients (c) of the bivariate B-spline representation of the
        surface along with the degree of the spline.
    fp : ndarray
        The weighted sum of squared residuals of the spline approximation.
    ier : int
        An integer flag about splrep success.  Success is indicated if
        ier<=0. If ier in [1,2,3] an error occurred but was not raised.
        Otherwise an error is raised.
    msg : str
        A message corresponding to the integer flag, ier.

    See Also
    --------
    splprep, splrep, splint, sproot, splev
    UnivariateSpline, BivariateSpline

    Notes
    -----
    See `bisplev` to evaluate the value of the B-spline given its tck
    representation.

    References
    ----------
    .. [1] Dierckx P.:An algorithm for surface fitting with spline functions
       Ima J. Numer. Anal. 1 (1981) 267-283.
    .. [2] Dierckx P.:An algorithm for surface fitting with spline functions
       report tw50, Dept. Computer Science,K.U.Leuven, 1980.
    .. [3] Dierckx P.:Curve and surface fitting with splines, Monographs on
       Numerical Analysis, Oxford University Press, 1993.

    """
    if task == 1 and cache is None:
        raise ValueError("Must call splrep with cache argument for task=1")
    if task <= 0 and cache is None:
        cache = {'t': array([], float), 'wrk': array([], float),
                 'iwrk': array([], intc)}
    x, y, z = map(ravel, [x, y, z])  # ensure 1-d arrays.
    m = len(x)
    if not (m == len(y) == len(z)):
        raise TypeError('len(x)==len(y)==len(z) must hold.')
    if w is None:
        w = ones(m, float)
    else:
        w = atleast_1d(w)
    if not len(w) == m:
        raise TypeError('len(w)=%d is not equal to m=%d' % (len(w), m))
    if xb is None:
        xb = x.min()
    if xe is None:
        xe = x.max()
    if yb is None:
        yb = y.min()
    if ye is None:
        ye = y.max()
    if not (-1 <= task <= 1):
        raise TypeError('task must be -1, 0 or 1')
    if s is None:
        s = m - sqrt(2*m)
    if tx is None and task == -1:
        raise TypeError('Knots_x must be given for task=-1')
    if tx is not None:
        _surfit_cache['tx'] = atleast_1d(tx)
    nx = len(_surfit_cache['tx'])
    if ty is None and task == -1:
        raise TypeError('Knots_y must be given for task=-1')
    if ty is not None:
        _surfit_cache['ty'] = atleast_1d(ty)
    ny = len(_surfit_cache['ty'])
    if task == -1 and nx < 2*kx+2:
        raise TypeError('There must be at least 2*kx+2 knots_x for task=-1')
    if task == -1 and ny < 2*ky+2:
        raise TypeError('There must be at least 2*ky+2 knots_x for task=-1')
    if not ((1 <= kx <= 5) and (1 <= ky <= 5)):
        raise TypeError('Given degree of the spline (kx,ky=%d,%d) is not '
                        'supported. (1<=k<=5)' % (kx, ky))
    if m < (kx + 1)*(ky + 1):
        raise TypeError('m >= (kx+1)(ky+1) must hold')
    if nxest is None:
        nxest = int(kx + sqrt(m/2))
    if nyest is None:
        nyest = int(ky + sqrt(m/2))
    nxest, nyest = max(nxest, 2*kx + 3), max(nyest, 2*ky + 3)
    if task >= 0 and s == 0:
        nxest = int(kx + sqrt(3*m))
        nyest = int(ky + sqrt(3*m))
    if task == -1:
        _surfit_cache['tx'] = atleast_1d(tx)
        _surfit_cache['ty'] = atleast_1d(ty)
    tx, ty = _surfit_cache['tx'], _surfit_cache['ty']
    wrk = _surfit_cache['wrk']
    u = nxest - kx - 1
    v = nyest - ky - 1
    km = max(kx, ky) + 1
    ne = max(nxest, nyest)
    bx, by = kx*v + ky + 1, ky*u + kx + 1
    b1, b2 = bx, bx + v - ky
    if bx > by:
        b1, b2 = by, by + u - kx
    msg = "Too many data points to interpolate"
    lwrk1 = _intc_overflow(u*v*(2 + b1 + b2) +
                           2*(u + v + km*(m + ne) + ne - kx - ky) + b2 + 1,
                           msg=msg)
    lwrk2 = _intc_overflow(u*v*(b2 + 1) + b2, msg=msg)
    tx, ty, c, o = _fitpack._surfit(x, y, z, w, xb, xe, yb, ye, kx, ky,
                                    task, s, eps, tx, ty, nxest, nyest,
                                    wrk, lwrk1, lwrk2)
    cache['tx'] = tx
    cache['ty'] = ty
    cache['wrk'] = o['wrk']
    ier, fp = o['ier'], o['fp']
    tck = [tx, ty, c, kx, ky]

    ierm = min(11, max(-3, ier))
    if ierm <= 0 and not quiet:
        _mess = (_iermess2[ierm][0] +
                 "\tkx,ky=%d,%d nx,ny=%d,%d m=%d fp=%f s=%f" %
                 (kx, ky, len(tx), len(ty), m, fp, s))
        warnings.warn(RuntimeWarning(_mess))
    if ierm > 0 and not full_output:
        if ier in [1, 2, 3, 4, 5]:
            _mess = ("\n\tkx,ky=%d,%d nx,ny=%d,%d m=%d fp=%f s=%f" %
                     (kx, ky, len(tx), len(ty), m, fp, s))
            warnings.warn(RuntimeWarning(_iermess2[ierm][0] + _mess))
        else:
            try:
                raise _iermess2[ierm][1](_iermess2[ierm][0])
            except KeyError:
                raise _iermess2['unknown'][1](_iermess2['unknown'][0])
    if full_output:
        try:
            return tck, fp, ier, _iermess2[ierm][0]
        except KeyError:
            return tck, fp, ier, _iermess2['unknown'][0]
    else:
        return tck