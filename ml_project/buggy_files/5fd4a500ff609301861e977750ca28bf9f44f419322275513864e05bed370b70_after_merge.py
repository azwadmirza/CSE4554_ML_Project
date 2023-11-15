    def fit(cls, x, y, deg, domain=None, rcond=None, full=False, w=None,
        window=None):
        """Least squares fit to data.

        Return a series instance that is the least squares fit to the data
        `y` sampled at `x`. The domain of the returned instance can be
        specified and this will often result in a superior fit with less
        chance of ill conditioning.

        Parameters
        ----------
        x : array_like, shape (M,)
            x-coordinates of the M sample points ``(x[i], y[i])``.
        y : array_like, shape (M,) or (M, K)
            y-coordinates of the sample points. Several data sets of sample
            points sharing the same x-coordinates can be fitted at once by
            passing in a 2D-array that contains one dataset per column.
        deg : int
            Degree of the fitting polynomial.
        domain : {None, [beg, end], []}, optional
            Domain to use for the returned series. If ``None``,
            then a minimal domain that covers the points `x` is chosen.  If
            ``[]`` the class domain is used. The default value was the
            class domain in NumPy 1.4 and ``None`` in later versions.
            The ``[]`` option was added in numpy 1.5.0.
        rcond : float, optional
            Relative condition number of the fit. Singular values smaller
            than this relative to the largest singular value will be
            ignored. The default value is len(x)*eps, where eps is the
            relative precision of the float type, about 2e-16 in most
            cases.
        full : bool, optional
            Switch determining nature of return value. When it is False
            (the default) just the coefficients are returned, when True
            diagnostic information from the singular value decomposition is
            also returned.
        w : array_like, shape (M,), optional
            Weights. If not None the contribution of each point
            ``(x[i],y[i])`` to the fit is weighted by `w[i]`. Ideally the
            weights are chosen so that the errors of the products
            ``w[i]*y[i]`` all have the same variance.  The default value is
            None.

            .. versionadded:: 1.5.0
        window : {[beg, end]}, optional
            Window to use for the returned series. The default
            value is the default class domain

            .. versionadded:: 1.6.0

        Returns
        -------
        new_series : series
            A series that represents the least squares fit to the data and
            has the domain specified in the call.

        [resid, rank, sv, rcond] : list
            These values are only returned if `full` = True

            resid -- sum of squared residuals of the least squares fit
            rank -- the numerical rank of the scaled Vandermonde matrix
            sv -- singular values of the scaled Vandermonde matrix
            rcond -- value of `rcond`.

            For more details, see `linalg.lstsq`.

        """
        if domain is None:
            domain = pu.getdomain(x)
        elif isinstance(domain, list) and len(domain) == 0:
            domain = cls.domain

        if window is None:
            window = cls.window

        xnew = pu.mapdomain(x, domain, window)
        res = cls._fit(xnew, y, deg, w=w, rcond=rcond, full=full)
        if full:
            [coef, status] = res
            return cls(coef, domain=domain, window=window), status
        else:
            coef = res
            return cls(coef, domain=domain, window=window)