def steadystate(A, c_op_list=[], method='direct', solver=None, **kwargs):
    """Calculates the steady state for quantum evolution subject to the
    supplied Hamiltonian or Liouvillian operator and (if given a Hamiltonian) a
    list of collapse operators.

    If the user passes a Hamiltonian then it, along with the list of collapse
    operators, will be converted into a Liouvillian operator in Lindblad form.

    Parameters
    ----------
    A : qobj
        A Hamiltonian or Liouvillian operator.

    c_op_list : list
        A list of collapse operators.

    solver : str {None, 'scipy', 'mkl'}
        Selects the sparse solver to use.  Default is auto-select
        based on the availability of the MKL library.

    method : str {'direct', 'eigen', 'iterative-gmres',
                  'iterative-lgmres', 'iterative-bicgstab', 'svd', 'power',
                  'power-gmres', 'power-lgmres', 'power-bicgstab'}
        Method for solving the underlying linear equation. Direct LU solver
        'direct' (default), sparse eigenvalue problem 'eigen',
        iterative GMRES method 'iterative-gmres', iterative LGMRES method
        'iterative-lgmres', iterative BICGSTAB method 'iterative-bicgstab',
        SVD 'svd' (dense), or inverse-power method 'power'. The iterative
        power methods 'power-gmres', 'power-lgmres', 'power-bicgstab' use
        the same solvers as their direct counterparts.

    return_info : bool, optional, default = False
        Return a dictionary of solver-specific infomation about the
        solution and how it was obtained.

    sparse : bool, optional, default = True
        Solve for the steady state using sparse algorithms. If set to False,
        the underlying Liouvillian operator will be converted into a dense
        matrix. Use only for 'smaller' systems.

    use_rcm : bool, optional, default = False
        Use reverse Cuthill-Mckee reordering to minimize fill-in in the
        LU factorization of the Liouvillian.

    use_wbm : bool, optional, default = False
        Use Weighted Bipartite Matching reordering to make the Liouvillian
        diagonally dominant.  This is useful for iterative preconditioners
        only, and is set to ``True`` by default when finding a preconditioner.

    weight : float, optional
        Sets the size of the elements used for adding the unity trace condition
        to the linear solvers.  This is set to the average abs value of the
        Liouvillian elements if not specified by the user.

    max_iter_refine : int {10}
        MKL ONLY. Max. number of iterative refinements to perform.

    scaling_vectors : bool {True, False}
        MKL ONLY.  Scale matrix to unit norm columns and rows.

    weighted_matching : bool {True, False}
        MKL ONLY.  Use weighted matching to better condition diagonal.

    x0 : ndarray, optional
        ITERATIVE ONLY. Initial guess for solution vector.

    maxiter : int, optional, default=1000
        ITERATIVE ONLY. Maximum number of iterations to perform.

    tol : float, optional, default=1e-12
        ITERATIVE ONLY. Tolerance used for terminating solver.

    mtol : float, optional, default=None
        ITERATIVE 'power' methods ONLY. Tolerance for lu solve method.
        If None given then `max(0.1*tol, 1e-15)` is used

    matol : float, optional, default=1e-15
        ITERATIVE ONLY. Absolute tolerance for lu solve method.

    permc_spec : str, optional, default='COLAMD'
        ITERATIVE ONLY. Column ordering used internally by superLU for the
        'direct' LU decomposition method. Options include 'COLAMD' and
        'NATURAL'. If using RCM then this is set to 'NATURAL' automatically
        unless explicitly specified.

    use_precond : bool optional, default = False
        ITERATIVE ONLY. Use an incomplete sparse LU decomposition as a
        preconditioner for the 'iterative' GMRES and BICG solvers.
        Speeds up convergence time by orders of magnitude in many cases.

    M : {sparse matrix, dense matrix, LinearOperator}, optional
        ITERATIVE ONLY. Preconditioner for A. The preconditioner should
        approximate the inverse of A. Effective preconditioning can
        dramatically improve the rate of convergence for iterative methods.
        If no preconditioner is given and ``use_precond = True``, then one
        is generated automatically.

    fill_factor : float, optional, default = 100
        ITERATIVE ONLY. Specifies the fill ratio upper bound (>=1) of the iLU
        preconditioner.  Lower values save memory at the cost of longer
        execution times and a possible singular factorization.

    drop_tol : float, optional, default = 1e-4
        ITERATIVE ONLY. Sets the threshold for the magnitude of preconditioner
        elements that should be dropped.  Can be reduced for a courser
        factorization at the cost of an increased number of iterations, and a
        possible singular factorization.

    diag_pivot_thresh : float, optional, default = None
        ITERATIVE ONLY. Sets the threshold between [0,1] for which diagonal
        elements are considered acceptable pivot points when using a
        preconditioner.  A value of zero forces the pivot to be the diagonal
        element.

    ILU_MILU : str, optional, default = 'smilu_2'
        ITERATIVE ONLY. Selects the incomplete LU decomposition method
        algoithm used in creating the preconditoner. Should only be used by
        advanced users.

    Returns
    -------
    dm : qobj
        Steady state density matrix.
    info : dict, optional
        Dictionary containing solver-specific information about the solution.

    Notes
    -----
    The SVD method works only for dense operators (i.e. small systems).

    """
    if solver is None:
        solver = 'scipy'
        if settings.has_mkl:
            if method in ['direct', 'power']:
                solver = 'mkl'
    elif solver == 'mkl' and \
            (method not in ['direct', 'power']):
        raise Exception('MKL solver only for direct or power methods.')

    elif solver not in ['scipy', 'mkl']:
        raise Exception('Invalid solver kwarg.')

    if solver == 'scipy':
        ss_args = _default_steadystate_args()
    elif solver == 'mkl':
        ss_args = _mkl_steadystate_args()
    else:
        raise Exception('Invalid solver keyword argument.')
    ss_args['method'] = method
    ss_args['info']['solver'] = ss_args['solver']
    ss_args['info']['method'] = ss_args['method']

    for key in kwargs.keys():
        if key in ss_args.keys():
            ss_args[key] = kwargs[key]
        else:
            raise Exception(
                "Invalid keyword argument '"+key+"' passed to steadystate.")

    # Set column perm to NATURAL if using RCM and not specified by user
    if ss_args['use_rcm'] and ('permc_spec' not in kwargs.keys()):
        ss_args['permc_spec'] = 'NATURAL'

    # Create & check Liouvillian
    A = _steadystate_setup(A, c_op_list)

    # Set weight parameter to avg abs val in L if not set explicitly
    if 'weight' not in kwargs.keys():
        ss_args['weight'] = np.mean(np.abs(A.data.data.max()))
        ss_args['info']['weight'] = ss_args['weight']

    if ss_args['method'] == 'direct':
        if (ss_args['solver'] == 'scipy' and ss_args['sparse']) \
                or ss_args['solver'] == 'mkl':
            return _steadystate_direct_sparse(A, ss_args)
        else:
            return _steadystate_direct_dense(A, ss_args)

    elif ss_args['method'] == 'eigen':
        return _steadystate_eigen(A, ss_args)

    elif ss_args['method'] in ['iterative-gmres',
                               'iterative-lgmres', 'iterative-bicgstab']:
        return _steadystate_iterative(A, ss_args)

    elif ss_args['method'] == 'svd':
        return _steadystate_svd_dense(A, ss_args)

    elif ss_args['method'] in ['power', 'power-gmres',
                               'power-lgmres', 'power-bicgstab']:
        return _steadystate_power(A, ss_args)

    else:
        raise ValueError('Invalid method argument for steadystate.')