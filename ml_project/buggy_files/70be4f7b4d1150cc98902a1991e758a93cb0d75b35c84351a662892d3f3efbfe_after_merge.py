def _report_nonhermitian(M, name):
    """
    Report if `M` is not a hermitian matrix given its type.
    """
    from scipy.linalg import norm

    md = M - M.T.conj()

    nmd = norm(md, 1)
    tol = 10 * np.finfo(M.dtype).eps
    tol = max(tol, tol * norm(M, 1))
    if nmd > tol:
        print('matrix %s of the type %s is not sufficiently Hermitian:'
              % (name, M.dtype))
        print('condition: %.e < %e' % (nmd, tol))