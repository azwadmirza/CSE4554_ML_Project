def _steadystate_direct_sparse(L, ss_args):
    """
    Direct solver that uses scipy sparse matrices
    """
    if settings.debug:
        logger.debug('Starting direct LU solver.')

    dims = L.dims[0]
    n = int(np.sqrt(L.shape[0]))
    b = np.zeros(n ** 2, dtype=complex)
    b[0] = ss_args['weight']

    if ss_args['solver'] == 'mkl':
        has_mkl = 1
    else:
        has_mkl = 0
    
    L, perm, perm2, rev_perm, ss_args = _steadystate_LU_liouvillian(L, ss_args, has_mkl)
    if np.any(perm):
        b = b[np.ix_(perm,)]
    if np.any(perm2):
        b = b[np.ix_(perm2,)]

    if ss_args['solver'] == 'scipy':
        ss_args['info']['permc_spec'] = ss_args['permc_spec']
        ss_args['info']['drop_tol'] = ss_args['drop_tol']
        ss_args['info']['diag_pivot_thresh'] = ss_args['diag_pivot_thresh']
        ss_args['info']['fill_factor'] = ss_args['fill_factor']
        ss_args['info']['ILU_MILU'] = ss_args['ILU_MILU']

    if not ss_args['solver'] == 'mkl':
        # Use superLU solver
        orig_nnz = L.nnz
        _direct_start = time.time()
        lu = splu(L, permc_spec=ss_args['permc_spec'],
                  diag_pivot_thresh=ss_args['diag_pivot_thresh'],
                  options=dict(ILU_MILU=ss_args['ILU_MILU']))
        v = lu.solve(b)
        _direct_end = time.time()
        ss_args['info']['solution_time'] = _direct_end - _direct_start
        if (settings.debug or ss_args['return_info']) and _scipy_check:
            L_nnz = lu.L.nnz
            U_nnz = lu.U.nnz
            ss_args['info']['l_nnz'] = L_nnz
            ss_args['info']['u_nnz'] = U_nnz
            ss_args['info']['lu_fill_factor'] = (L_nnz + U_nnz)/L.nnz
            if settings.debug:
                logger.debug('L NNZ: %i ; U NNZ: %i' % (L_nnz, U_nnz))
                logger.debug('Fill factor: %f' % ((L_nnz + U_nnz)/orig_nnz))

    else: # Use MKL solver
        if len(ss_args['info']['perm']) !=0:
            in_perm = np.arange(n**2, dtype=np.int32)
        else:
            in_perm = None
        _direct_start = time.time()
        v = mkl_spsolve(L, b, perm = in_perm, verbose = ss_args['verbose'],
                        max_iter_refine=ss_args['max_iter_refine'],
                        scaling_vectors=ss_args['scaling_vectors'],
                        weighted_matching=ss_args['weighted_matching'])
        _direct_end = time.time()
        ss_args['info']['solution_time'] = _direct_end-_direct_start

    if ss_args['return_info']:
        ss_args['info']['residual_norm'] = la.norm(b - L*v, np.inf)
        ss_args['info']['max_iter_refine'] = ss_args['max_iter_refine']
        ss_args['info']['scaling_vectors'] = ss_args['scaling_vectors']
        ss_args['info']['weighted_matching'] = ss_args['weighted_matching']

    if ss_args['use_rcm']:
        v = v[np.ix_(rev_perm,)]

    data = dense2D_to_fastcsr_fmode(vec2mat(v), n, n)
    data = 0.5 * (data + data.H)
    if ss_args['return_info']:
        return Qobj(data, dims=dims, isherm=True), ss_args['info']
    else:
        return Qobj(data, dims=dims, isherm=True)