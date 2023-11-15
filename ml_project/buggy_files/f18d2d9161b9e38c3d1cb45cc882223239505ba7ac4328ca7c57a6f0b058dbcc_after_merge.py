def cdist(XA, XB, metric='euclidean', p=None, V=None, VI=None, w=None):
    """
    Computes distance between each pair of the two collections of inputs.

    See Notes for common calling conventions.

    Parameters
    ----------
    XA : ndarray
        An :math:`m_A` by :math:`n` array of :math:`m_A`
        original observations in an :math:`n`-dimensional space.
        Inputs are converted to float type.
    XB : ndarray
        An :math:`m_B` by :math:`n` array of :math:`m_B`
        original observations in an :math:`n`-dimensional space.
        Inputs are converted to float type.
    metric : str or callable, optional
        The distance metric to use.  If a string, the distance function can be
        'braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation',
        'cosine', 'dice', 'euclidean', 'hamming', 'jaccard', 'kulsinski',
        'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto', 'russellrao',
        'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
        'wminkowski', 'yule'.
    p : double, optional
        The p-norm to apply
        Only for Minkowski, weighted and unweighted. Default: 2.
    w : ndarray, optional
        The weight vector.
        Only for weighted Minkowski. Mandatory
    V : ndarray, optional
        The variance vector
        Only for standardized Euclidean. Default: var(vstack([XA, XB]), axis=0, ddof=1)
    VI : ndarray, optional
        The inverse of the covariance matrix
        Only for Mahalanobis. Default: inv(cov(vstack([XA, XB]).T)).T

    Returns
    -------
    Y : ndarray
        A :math:`m_A` by :math:`m_B` distance matrix is returned.
        For each :math:`i` and :math:`j`, the metric
        ``dist(u=XA[i], v=XB[j])`` is computed and stored in the
        :math:`ij` th entry.

    Raises
    ------
    ValueError
        An exception is thrown if `XA` and `XB` do not have
        the same number of columns.

    Notes
    -----
    The following are common calling conventions:

    1. ``Y = cdist(XA, XB, 'euclidean')``

       Computes the distance between :math:`m` points using
       Euclidean distance (2-norm) as the distance metric between the
       points. The points are arranged as :math:`m`
       :math:`n`-dimensional row vectors in the matrix X.

    2. ``Y = cdist(XA, XB, 'minkowski', p)``

       Computes the distances using the Minkowski distance
       :math:`||u-v||_p` (:math:`p`-norm) where :math:`p \\geq 1`.

    3. ``Y = cdist(XA, XB, 'cityblock')``

       Computes the city block or Manhattan distance between the
       points.

    4. ``Y = cdist(XA, XB, 'seuclidean', V=None)``

       Computes the standardized Euclidean distance. The standardized
       Euclidean distance between two n-vectors ``u`` and ``v`` is

       .. math::

          \\sqrt{\\sum {(u_i-v_i)^2 / V[x_i]}}.

       V is the variance vector; V[i] is the variance computed over all
       the i'th components of the points. If not passed, it is
       automatically computed.

    5. ``Y = cdist(XA, XB, 'sqeuclidean')``

       Computes the squared Euclidean distance :math:`||u-v||_2^2` between
       the vectors.

    6. ``Y = cdist(XA, XB, 'cosine')``

       Computes the cosine distance between vectors u and v,

       .. math::

          1 - \\frac{u \\cdot v}
                   {{||u||}_2 {||v||}_2}

       where :math:`||*||_2` is the 2-norm of its argument ``*``, and
       :math:`u \\cdot v` is the dot product of :math:`u` and :math:`v`.

    7. ``Y = cdist(XA, XB, 'correlation')``

       Computes the correlation distance between vectors u and v. This is

       .. math::

          1 - \\frac{(u - \\bar{u}) \\cdot (v - \\bar{v})}
                   {{||(u - \\bar{u})||}_2 {||(v - \\bar{v})||}_2}

       where :math:`\\bar{v}` is the mean of the elements of vector v,
       and :math:`x \\cdot y` is the dot product of :math:`x` and :math:`y`.


    8. ``Y = cdist(XA, XB, 'hamming')``

       Computes the normalized Hamming distance, or the proportion of
       those vector elements between two n-vectors ``u`` and ``v``
       which disagree. To save memory, the matrix ``X`` can be of type
       boolean.

    9. ``Y = cdist(XA, XB, 'jaccard')``

       Computes the Jaccard distance between the points. Given two
       vectors, ``u`` and ``v``, the Jaccard distance is the
       proportion of those elements ``u[i]`` and ``v[i]`` that
       disagree where at least one of them is non-zero.

    10. ``Y = cdist(XA, XB, 'chebyshev')``

       Computes the Chebyshev distance between the points. The
       Chebyshev distance between two n-vectors ``u`` and ``v`` is the
       maximum norm-1 distance between their respective elements. More
       precisely, the distance is given by

       .. math::

          d(u,v) = \\max_i {|u_i-v_i|}.

    11. ``Y = cdist(XA, XB, 'canberra')``

       Computes the Canberra distance between the points. The
       Canberra distance between two points ``u`` and ``v`` is

       .. math::

         d(u,v) = \\sum_i \\frac{|u_i-v_i|}
                              {|u_i|+|v_i|}.

    12. ``Y = cdist(XA, XB, 'braycurtis')``

       Computes the Bray-Curtis distance between the points. The
       Bray-Curtis distance between two points ``u`` and ``v`` is


       .. math::

            d(u,v) = \\frac{\\sum_i (|u_i-v_i|)}
                          {\\sum_i (|u_i+v_i|)}

    13. ``Y = cdist(XA, XB, 'mahalanobis', VI=None)``

       Computes the Mahalanobis distance between the points. The
       Mahalanobis distance between two points ``u`` and ``v`` is
       :math:`\\sqrt{(u-v)(1/V)(u-v)^T}` where :math:`(1/V)` (the ``VI``
       variable) is the inverse covariance. If ``VI`` is not None,
       ``VI`` will be used as the inverse covariance matrix.

    14. ``Y = cdist(XA, XB, 'yule')``

       Computes the Yule distance between the boolean
       vectors. (see `yule` function documentation)

    15. ``Y = cdist(XA, XB, 'matching')``

       Synonym for 'hamming'.

    16. ``Y = cdist(XA, XB, 'dice')``

       Computes the Dice distance between the boolean vectors. (see
       `dice` function documentation)

    17. ``Y = cdist(XA, XB, 'kulsinski')``

       Computes the Kulsinski distance between the boolean
       vectors. (see `kulsinski` function documentation)

    18. ``Y = cdist(XA, XB, 'rogerstanimoto')``

       Computes the Rogers-Tanimoto distance between the boolean
       vectors. (see `rogerstanimoto` function documentation)

    19. ``Y = cdist(XA, XB, 'russellrao')``

       Computes the Russell-Rao distance between the boolean
       vectors. (see `russellrao` function documentation)

    20. ``Y = cdist(XA, XB, 'sokalmichener')``

       Computes the Sokal-Michener distance between the boolean
       vectors. (see `sokalmichener` function documentation)

    21. ``Y = cdist(XA, XB, 'sokalsneath')``

       Computes the Sokal-Sneath distance between the vectors. (see
       `sokalsneath` function documentation)


    22. ``Y = cdist(XA, XB, 'wminkowski')``

       Computes the weighted Minkowski distance between the
       vectors. (see `wminkowski` function documentation)

    23. ``Y = cdist(XA, XB, f)``

       Computes the distance between all pairs of vectors in X
       using the user supplied 2-arity function f. For example,
       Euclidean distance between the vectors could be computed
       as follows::

         dm = cdist(XA, XB, lambda u, v: np.sqrt(((u-v)**2).sum()))

       Note that you should avoid passing a reference to one of
       the distance functions defined in this library. For example,::

         dm = cdist(XA, XB, sokalsneath)

       would calculate the pair-wise distances between the vectors in
       X using the Python function `sokalsneath`. This would result in
       sokalsneath being called :math:`{n \\choose 2}` times, which
       is inefficient. Instead, the optimized C version is more
       efficient, and we call it using the following syntax::

         dm = cdist(XA, XB, 'sokalsneath')

    Examples
    --------
    Find the Euclidean distances between four 2-D coordinates:

    >>> from scipy.spatial import distance
    >>> coords = [(35.0456, -85.2672),
    ...           (35.1174, -89.9711),
    ...           (35.9728, -83.9422),
    ...           (36.1667, -86.7833)]
    >>> distance.cdist(coords, coords, 'euclidean')
    array([[ 0.    ,  4.7044,  1.6172,  1.8856],
           [ 4.7044,  0.    ,  6.0893,  3.3561],
           [ 1.6172,  6.0893,  0.    ,  2.8477],
           [ 1.8856,  3.3561,  2.8477,  0.    ]])


    Find the Manhattan distance from a 3-D point to the corners of the unit
    cube:

    >>> a = np.array([[0, 0, 0],
    ...               [0, 0, 1],
    ...               [0, 1, 0],
    ...               [0, 1, 1],
    ...               [1, 0, 0],
    ...               [1, 0, 1],
    ...               [1, 1, 0],
    ...               [1, 1, 1]])
    >>> b = np.array([[ 0.1,  0.2,  0.4]])
    >>> distance.cdist(a, b, 'cityblock')
    array([[ 0.7],
           [ 0.9],
           [ 1.3],
           [ 1.5],
           [ 1.5],
           [ 1.7],
           [ 2.1],
           [ 2.3]])

    """
    # You can also call this as:
    #     Y = cdist(XA, XB, 'test_abc')
    # where 'abc' is the metric being tested.  This computes the distance
    # between all pairs of vectors in XA and XB using the distance metric 'abc'
    # but with a more succinct, verifiable, but less efficient implementation.

    # Store input arguments to check whether we can modify later.
    input_XA, input_XB = XA, XB

    XA = np.asarray(XA, order='c')
    XB = np.asarray(XB, order='c')

    # The C code doesn't do striding.
    XA = _copy_array_if_base_present(XA)
    XB = _copy_array_if_base_present(XB)

    s = XA.shape
    sB = XB.shape

    if len(s) != 2:
        raise ValueError('XA must be a 2-dimensional array.')
    if len(sB) != 2:
        raise ValueError('XB must be a 2-dimensional array.')
    if s[1] != sB[1]:
        raise ValueError('XA and XB must have the same number of columns '
                         '(i.e. feature dimension.)')

    mA = s[0]
    mB = sB[0]
    n = s[1]
    dm = np.zeros((mA, mB), dtype=np.double)

    # validate input for multi-args metrics
    if(metric in ['minkowski', 'mi', 'm', 'pnorm', 'test_minkowski'] or
       metric == minkowski):
        p = _validate_minkowski_args(p)
        _filter_deprecated_kwargs(w=w, V=V, VI=VI)
    elif(metric in ['wminkowski', 'wmi', 'wm', 'wpnorm', 'test_wminkowski'] or
         metric == wminkowski):
        p, w = _validate_wminkowski_args(p, w)
        _filter_deprecated_kwargs(V=V, VI=VI)
    elif(metric in ['seuclidean', 'se', 's', 'test_seuclidean'] or
         metric == seuclidean):
        V = _validate_seuclidean_args(np.vstack([XA, XB]), n, V)
        _filter_deprecated_kwargs(p=p, w=w, VI=VI)
    elif(metric in ['mahalanobis', 'mahal', 'mah', 'test_mahalanobis'] or
         metric == mahalanobis):
        VI = _validate_mahalanobis_args(np.vstack([XA, XB]), mA + mB, n, VI)
        _filter_deprecated_kwargs(p=p, w=w, V=V)
    else:
        _filter_deprecated_kwargs(p=p, w=w, V=V, VI=VI)

    if callable(metric):
        # metrics that expects only doubles:
        if metric in [braycurtis, canberra, chebyshev, cityblock, correlation,
                      cosine, euclidean, mahalanobis, minkowski, sqeuclidean,
                      seuclidean, wminkowski]:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
        # metrics that expects only bools:
        elif metric in [dice, kulsinski, rogerstanimoto, russellrao,
                        sokalmichener, sokalsneath, yule]:
            XA = _convert_to_bool(XA)
            XB = _convert_to_bool(XB)
        # metrics that may receive multiple types:
        elif metric in [matching, hamming, jaccard]:
            if XA.dtype == bool:
                XA = _convert_to_bool(XA)
                XB = _convert_to_bool(XB)
            else:
                XA = _convert_to_double(XA)
                XB = _convert_to_double(XB)

        # metrics that expects multiple args
        if metric == minkowski:
            metric = partial(minkowski, p=p)
        elif metric == wminkowski:
            metric = partial(wminkowski, p=p, w=w)
        elif metric == seuclidean:
            metric = partial(seuclidean, V=V)
        elif metric == mahalanobis:
            metric = partial(mahalanobis, VI=VI)

        for i in xrange(0, mA):
            for j in xrange(0, mB):
                dm[i, j] = metric(XA[i, :], XB[j, :])

    elif isinstance(metric, string_types):
        mstr = metric.lower()

        try:
            validate, cdist_fn = _SIMPLE_CDIST[mstr]
            XA = validate(XA)
            XB = validate(XB)
            cdist_fn(XA, XB, dm)
            return dm
        except KeyError:
            pass

        if mstr in ['matching', 'hamming', 'hamm', 'ha', 'h']:
            if XA.dtype == bool:
                XA = _convert_to_bool(XA)
                XB = _convert_to_bool(XB)
                _distance_wrap.cdist_hamming_bool_wrap(XA, XB, dm)
            else:
                XA = _convert_to_double(XA)
                XB = _convert_to_double(XB)
                _distance_wrap.cdist_hamming_wrap(XA, XB, dm)
        elif mstr in ['jaccard', 'jacc', 'ja', 'j']:
            if XA.dtype == bool:
                XA = _convert_to_bool(XA)
                XB = _convert_to_bool(XB)
                _distance_wrap.cdist_jaccard_bool_wrap(XA, XB, dm)
            else:
                XA = _convert_to_double(XA)
                XB = _convert_to_double(XB)
                _distance_wrap.cdist_jaccard_wrap(XA, XB, dm)
        elif mstr in ['minkowski', 'mi', 'm', 'pnorm']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            _distance_wrap.cdist_minkowski_wrap(XA, XB, dm, p=p)
        elif mstr in ['wminkowski', 'wmi', 'wm', 'wpnorm']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            _distance_wrap.cdist_weighted_minkowski_wrap(XA, XB, dm, p=p, w=w)
        elif mstr in ['seuclidean', 'se', 's']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            _distance_wrap.cdist_seuclidean_wrap(XA, XB, dm, V=V)
        elif mstr in ['cosine', 'cos']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            _cosine_cdist(XA, XB, dm)
        elif mstr in ['correlation', 'co']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            XA = XA.copy() if XA is input_XA else XA
            XB = XB.copy() if XB is input_XB else XB
            XA -= XA.mean(axis=1)[:, np.newaxis]
            XB -= XB.mean(axis=1)[:, np.newaxis]
            _cosine_cdist(XA, XB, dm)
        elif mstr in ['mahalanobis', 'mahal', 'mah']:
            XA = _convert_to_double(XA)
            XB = _convert_to_double(XB)
            # sqrt((u-v)V^(-1)(u-v)^T)
            _distance_wrap.cdist_mahalanobis_wrap(XA, XB, dm, VI=VI)
        elif mstr.startswith("test_"):
            if mstr in _TEST_METRICS:
                kwargs = {"p":p, "w":w, "V":V, "VI":VI}
                dm = cdist(XA, XB, _TEST_METRICS[mstr], **kwargs)
            else:
                raise ValueError('Unknown "Test" Distance Metric: %s' % mstr[5:])
        else:
            raise ValueError('Unknown Distance Metric: %s' % mstr)
    else:
        raise TypeError('2nd argument metric must be a string identifier '
                        'or a function.')
    return dm