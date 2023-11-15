def _solve_simplex(T, n, basis, maxiter=1000, phase=2, callback=None,
                   tol=1.0E-12, nit0=0, bland=False):
    """
    Solve a linear programming problem in "standard maximization form" using
    the Simplex Method.

    Minimize :math:`f = c^T x`

    subject to

    .. math::

        Ax = b
        x_i >= 0
        b_j >= 0

    Parameters
    ----------
    T : array_like
        A 2-D array representing the simplex T corresponding to the
        maximization problem.  It should have the form:

        [[A[0, 0], A[0, 1], ..., A[0, n_total], b[0]],
         [A[1, 0], A[1, 1], ..., A[1, n_total], b[1]],
         .
         .
         .
         [A[m, 0], A[m, 1], ..., A[m, n_total], b[m]],
         [c[0],   c[1], ...,   c[n_total],    0]]

        for a Phase 2 problem, or the form:

        [[A[0, 0], A[0, 1], ..., A[0, n_total], b[0]],
         [A[1, 0], A[1, 1], ..., A[1, n_total], b[1]],
         .
         .
         .
         [A[m, 0], A[m, 1], ..., A[m, n_total], b[m]],
         [c[0],   c[1], ...,   c[n_total],   0],
         [c'[0],  c'[1], ...,  c'[n_total],  0]]

         for a Phase 1 problem (a Problem in which a basic feasible solution is
         sought prior to maximizing the actual objective.  T is modified in
         place by _solve_simplex.
    n : int
        The number of true variables in the problem.
    basis : array
        An array of the indices of the basic variables, such that basis[i]
        contains the column corresponding to the basic variable for row i.
        Basis is modified in place by _solve_simplex
    maxiter : int
        The maximum number of iterations to perform before aborting the
        optimization.
    phase : int
        The phase of the optimization being executed.  In phase 1 a basic
        feasible solution is sought and the T has an additional row representing
        an alternate objective function.
    callback : callable, optional
        If a callback function is provided, it will be called within each
        iteration of the simplex algorithm. The callback must have the
        signature `callback(xk, **kwargs)` where xk is the current solution
        vector and kwargs is a dictionary containing the following::
        "T" : The current Simplex algorithm T
        "nit" : The current iteration.
        "pivot" : The pivot (row, column) used for the next iteration.
        "phase" : Whether the algorithm is in Phase 1 or Phase 2.
        "basis" : The indices of the columns of the basic variables.
    tol : float
        The tolerance which determines when a solution is "close enough" to
        zero in Phase 1 to be considered a basic feasible solution or close
        enough to positive to to serve as an optimal solution.
    nit0 : int
        The initial iteration number used to keep an accurate iteration total
        in a two-phase problem.
    bland : bool
        If True, choose pivots using Bland's rule [3].  In problems which
        fail to converge due to cycling, using Bland's rule can provide
        convergence at the expense of a less optimal path about the simplex.

    Returns
    -------
    res : OptimizeResult
        The optimization result represented as a ``OptimizeResult`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the optimizer exited successfully and
        ``message`` which describes the cause of the termination. Possible
        values for the ``status`` attribute are:
         0 : Optimization terminated successfully
         1 : Iteration limit reached
         2 : Problem appears to be infeasible
         3 : Problem appears to be unbounded

        See `OptimizeResult` for a description of other attributes.
    """
    nit = nit0
    complete = False

    if phase == 1:
        m = T.shape[0]-2
    elif phase == 2:
        m = T.shape[0]-1
    else:
        raise ValueError("Argument 'phase' to _solve_simplex must be 1 or 2")

    if len(basis[:m]) == 0:
        solution = np.zeros(T.shape[1] - 1, dtype=np.float64)
    else:
        solution = np.zeros(max(T.shape[1] - 1, max(basis[:m]) + 1),
                            dtype=np.float64)

    while not complete:
        # Find the pivot column
        pivcol_found, pivcol = _pivot_col(T, tol, bland)
        if not pivcol_found:
            pivcol = np.nan
            pivrow = np.nan
            status = 0
            complete = True
        else:
            # Find the pivot row
            pivrow_found, pivrow = _pivot_row(T, pivcol, phase, tol)
            if not pivrow_found:
                status = 3
                complete = True

        if callback is not None:
            solution[:] = 0
            solution[basis[:m]] = T[:m, -1]
            callback(solution[:n], **{"tableau": T,
                                      "phase":phase,
                                      "nit":nit,
                                      "pivot":(pivrow, pivcol),
                                      "basis":basis,
                                      "complete": complete and phase == 2})

        if not complete:
            if nit >= maxiter:
                # Iteration limit exceeded
                status = 1
                complete = True
            else:
                # variable represented by pivcol enters
                # variable in basis[pivrow] leaves
                basis[pivrow] = pivcol
                pivval = T[pivrow][pivcol]
                T[pivrow, :] = T[pivrow, :] / pivval
                for irow in range(T.shape[0]):
                    if irow != pivrow:
                        T[irow, :] = T[irow, :] - T[pivrow, :]*T[irow, pivcol]
                nit += 1

    return nit, status