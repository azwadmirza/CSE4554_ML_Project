def _steadystate_power(L, ss_args):
    """
    Inverse power method for steady state solving.
    """
    ss_args['info'].pop('weight', None)
    if settings.debug:
        logger.debug('Starting iterative inverse-power method solver.')
    tol = ss_args['tol']
    mtol = ss_args['mtol']
    if mtol is None:
        mtol = max(0.1*tol, 1e-15)
    maxiter = ss_args['maxiter']

    use_solver(assumeSortedIndices=True)
    rhoss = Qobj()
    sflag = issuper(L)
    if sflag:
        rhoss.dims = L.dims[0]
    else:
        rhoss.dims = [L.dims[0], 1]
    n = L.shape[0]
    # Build Liouvillian
    if ss_args['solver'] == 'mkl' and ss_args['method'] == 'power':
        has_mkl = 1
    else:
        has_mkl = 0
    L, perm, perm2, rev_perm, ss_args = _steadystate_power_liouvillian(L,
                                                                       ss_args,
                                                                       has_mkl)
    orig_nnz = L.nnz
    # start with all ones as RHS
    v = np.ones(n, dtype=complex)
    if ss_args['use_rcm']:
        v = v[np.ix_(perm2,)]

    # Do preconditioning
    if ss_args['solver'] == 'scipy':
        if ss_args['M'] is None and ss_args['use_precond'] and \
                ss_args['method'] in ['power-gmres',
                                      'power-lgmres',
                                      'power-bicgstab']:
            ss_args['M'], ss_args = _iterative_precondition(L, int(np.sqrt(n)),
                                                            ss_args)
            if ss_args['M'] is None:
                warnings.warn("Preconditioning failed. Continuing without.",
                              UserWarning)

    ss_iters = {'iter': 0}

    def _iter_count(r):
        ss_iters['iter'] += 1
        return

    _power_start = time.time()
    # Get LU factors
    if ss_args['method'] == 'power':
        if ss_args['solver'] == 'mkl':
            lu = mkl_splu(L, max_iter_refine=ss_args['max_iter_refine'],
                          scaling_vectors=ss_args['scaling_vectors'],
                          weighted_matching=ss_args['weighted_matching'])
        else:
            lu = splu(L, permc_spec=ss_args['permc_spec'],
                      diag_pivot_thresh=ss_args['diag_pivot_thresh'],
                      options=dict(ILU_MILU=ss_args['ILU_MILU']))

            if settings.debug and _scipy_check:
                L_nnz = lu.L.nnz
                U_nnz = lu.U.nnz
                logger.debug('L NNZ: %i ; U NNZ: %i' % (L_nnz, U_nnz))
                logger.debug('Fill factor: %f' % ((L_nnz+U_nnz)/orig_nnz))

    it = 0
    # FIXME: These atol keyword except checks can be removed once scipy 1.1
    # is a minimum requirement
    while (la.norm(L * v, np.inf) > tol) and (it < maxiter):
        check = 0
        if ss_args['method'] == 'power':
            v = lu.solve(v)
        elif ss_args['method'] == 'power-gmres':
            try:
                v, check = gmres(L, v, tol=mtol, atol=ss_args['matol'],
                                 M=ss_args['M'], x0=ss_args['x0'],
                                 restart=ss_args['restart'],
                                 maxiter=ss_args['maxiter'],
                                 callback=_iter_count)
            except TypeError as e:
                if "unexpected keyword argument 'atol'" in str(e):
                    v, check = gmres(L, v, tol=mtol,
                                     M=ss_args['M'], x0=ss_args['x0'],
                                     restart=ss_args['restart'],
                                     maxiter=ss_args['maxiter'],
                                     callback=_iter_count)

        elif ss_args['method'] == 'power-lgmres':
            try:
                v, check = lgmres(L, v, tol=mtol, atol=ss_args['matol'],
                                  M=ss_args['M'], x0=ss_args['x0'],
                                  maxiter=ss_args['maxiter'],
                                  callback=_iter_count)
            except TypeError as e:
                if "unexpected keyword argument 'atol'" in str(e):
                    v, check = lgmres(L, v, tol=mtol,
                                      M=ss_args['M'], x0=ss_args['x0'],
                                      maxiter=ss_args['maxiter'],
                                      callback=_iter_count)

        elif ss_args['method'] == 'power-bicgstab':
            try:
                v, check = bicgstab(L, v, tol=mtol, atol=ss_args['matol'],
                                    M=ss_args['M'], x0=ss_args['x0'],
                                    maxiter=ss_args['maxiter'],
                                    callback=_iter_count)
            except TypeError as e:
                if "unexpected keyword argument 'atol'" in str(e):
                    v, check = bicgstab(L, v, tol=mtol,
                                        M=ss_args['M'], x0=ss_args['x0'],
                                        maxiter=ss_args['maxiter'],
                                        callback=_iter_count)
        else:
            raise Exception("Invalid iterative solver method.")
        if check > 0:
            raise Exception("{} failed to find solution in "
                            "{} iterations.".format(ss_args['method'],
                                                    check))
        if check < 0:
            raise Exception("Breakdown in {}".format(ss_args['method']))
        v = v / la.norm(v, np.inf)
        it += 1
    if ss_args['method'] == 'power' and ss_args['solver'] == 'mkl':
        lu.delete()
        if ss_args['return_info']:
            ss_args['info']['max_iter_refine'] = ss_args['max_iter_refine']
            ss_args['info']['scaling_vectors'] = ss_args['scaling_vectors']
            ss_args['info']['weighted_matching'] = ss_args['weighted_matching']

    if it >= maxiter:
        raise Exception('Failed to find steady state after ' +
                        str(maxiter) + ' iterations')
    _power_end = time.time()
    ss_args['info']['solution_time'] = _power_end-_power_start
    ss_args['info']['iterations'] = it
    if ss_args['return_info']:
        ss_args['info']['residual_norm'] = la.norm(L*v, np.inf)
    if settings.debug:
        logger.debug('Number of iterations: %i' % it)

    if ss_args['use_rcm']:
        v = v[np.ix_(rev_perm,)]

    # normalise according to type of problem
    if sflag:
        trow = v[::rhoss.shape[0]+1]
        data = v / np.sum(trow)
    else:
        data = data / la.norm(v)

    data = dense2D_to_fastcsr_fmode(vec2mat(data),
                                    rhoss.shape[0],
                                    rhoss.shape[0])
    rhoss.data = 0.5 * (data + data.H)
    rhoss.isherm = True
    if ss_args['return_info']:
        return rhoss, ss_args['info']
    else:
        return rhoss