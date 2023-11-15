def _steadystate_iterative(L, ss_args):
    """
    Iterative steady state solver using the GMRES, LGMRES, or BICGSTAB
    algorithm and a sparse incomplete LU preconditioner.
    """
    ss_iters = {'iter': 0}

    def _iter_count(r):
        ss_iters['iter'] += 1
        return

    if settings.debug:
        logger.debug('Starting %s solver.' % ss_args['method'])

    dims = L.dims[0]
    n = int(np.sqrt(L.shape[0]))
    b = np.zeros(n ** 2)
    b[0] = ss_args['weight']

    L, perm, perm2, rev_perm, ss_args = _steadystate_LU_liouvillian(L, ss_args)
    if np.any(perm):
        b = b[np.ix_(perm,)]
    if np.any(perm2):
        b = b[np.ix_(perm2,)]

    use_solver(assumeSortedIndices=True)

    if ss_args['M'] is None and ss_args['use_precond']:
        ss_args['M'], ss_args = _iterative_precondition(L, n, ss_args)
        if ss_args['M'] is None:
            warnings.warn("Preconditioning failed. Continuing without.",
                          UserWarning)

    # Select iterative solver type
    _iter_start = time.time()
    # FIXME: These atol keyword except checks can be removed once scipy 1.1
    # is a minimum requirement
    if ss_args['method'] == 'iterative-gmres':
        try:
            v, check = gmres(L, b, tol=ss_args['tol'], atol=ss_args['matol'],
                             M=ss_args['M'], x0=ss_args['x0'],
                             restart=ss_args['restart'],
                             maxiter=ss_args['maxiter'],
                             callback=_iter_count)
        except TypeError as e:
            if "unexpected keyword argument 'atol'" in str(e):
                v, check = gmres(L, b, tol=ss_args['tol'],
                                 M=ss_args['M'], x0=ss_args['x0'],
                                 restart=ss_args['restart'],
                                 maxiter=ss_args['maxiter'],
                                 callback=_iter_count)

    elif ss_args['method'] == 'iterative-lgmres':
        try:
            v, check = lgmres(L, b, tol=ss_args['tol'], atol=ss_args['matol'],
                              M=ss_args['M'], x0=ss_args['x0'],
                              maxiter=ss_args['maxiter'],
                              callback=_iter_count)
        except TypeError as e:
            if "unexpected keyword argument 'atol'" in str(e):
                v, check = lgmres(L, b, tol=ss_args['tol'],
                                  M=ss_args['M'], x0=ss_args['x0'],
                                  maxiter=ss_args['maxiter'],
                                  callback=_iter_count)

    elif ss_args['method'] == 'iterative-bicgstab':
        try:
            v, check = bicgstab(L, b, tol=ss_args['tol'],
                                atol=ss_args['matol'],
                                M=ss_args['M'], x0=ss_args['x0'],
                                maxiter=ss_args['maxiter'],
                                callback=_iter_count)
        except TypeError as e:
            if "unexpected keyword argument 'atol'" in str(e):
                v, check = bicgstab(L, b, tol=ss_args['tol'],
                                    M=ss_args['M'], x0=ss_args['x0'],
                                    maxiter=ss_args['maxiter'],
                                    callback=_iter_count)
    else:
        raise Exception("Invalid iterative solver method.")
    _iter_end = time.time()

    ss_args['info']['iter_time'] = _iter_end - _iter_start
    if 'precond_time' in ss_args['info'].keys():
        ss_args['info']['solution_time'] = (ss_args['info']['iter_time'] +
                                            ss_args['info']['precond_time'])
    else:
        ss_args['info']['solution_time'] = ss_args['info']['iter_time']
    ss_args['info']['iterations'] = ss_iters['iter']
    if ss_args['return_info']:
        ss_args['info']['residual_norm'] = la.norm(b - L*v, np.inf)

    if settings.debug:
        logger.debug('Number of Iterations: %i' % ss_iters['iter'])
        logger.debug('Iteration. time: %f' % (_iter_end - _iter_start))

    if check > 0:
        raise Exception("Steadystate error: Did not reach tolerance after " +
                        str(ss_args['maxiter']) + " steps." +
                        "\nResidual norm: " +
                        str(ss_args['info']['residual_norm']))

    elif check < 0:
        raise Exception(
            "Steadystate error: Failed with fatal error: " + str(check) + ".")

    if ss_args['use_rcm']:
        v = v[np.ix_(rev_perm,)]

    data = vec2mat(v)
    data = 0.5 * (data + data.conj().T)
    if ss_args['return_info']:
        return Qobj(data, dims=dims, isherm=True), ss_args['info']
    else:
        return Qobj(data, dims=dims, isherm=True)