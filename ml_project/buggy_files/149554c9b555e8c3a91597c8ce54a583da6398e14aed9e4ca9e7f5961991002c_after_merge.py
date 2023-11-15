def _phase_one(A, b, maxiter, tol, maxupdate, mast, pivot):
    """
    The purpose of phase one is to find an initial basic feasible solution
    (BFS) to the original problem.

    Generates an auxiliary problem with a trivial BFS and an objective that
    minimizes infeasibility of the original problem. Solves the auxiliary
    problem using the main simplex routine (phase two). This either yields
    a BFS to the original problem or determines that the original problem is
    infeasible. If feasible, phase one detects redundant rows in the original
    constraint matrix and removes them, then chooses additional indices as
    necessary to complete a basis/BFS for the original problem.
    """

    m, n = A.shape
    status = 0

    # generate auxiliary problem to get initial BFS
    A, b, c, basis, x = _generate_auxiliary_problem(A, b)

    # solve auxiliary problem
    x, basis, status, iter_k = _phase_two(c, A, x, basis, maxiter,
                                          tol, maxupdate, mast, pivot)

    # check for infeasibility
    residual = c.dot(x)
    if status == 0 and residual > tol:
        status = 2

    # detect redundancy
    # TODO: consider removing this?
    B = A[:, basis]
    try:
        rank_revealer = solve(B, A[:, :n])
        z = _find_nonzero_rows(rank_revealer, tol)

        # eliminate redundancy
        A = A[z, :n]
        b = b[z]
    except (LinAlgError, LinAlgError2):
        status = 4

    # form solution to original problem
    x = x[:n]
    m = A.shape[0]
    basis = basis[basis < n]

    # if feasible, choose additional indices to complete basis
    if status == 0 and len(basis) < m:
        basis = _get_more_basis_columns(A, basis)

    return x, basis, A, b, residual, status, iter_k