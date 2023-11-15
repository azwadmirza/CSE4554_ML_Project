def _report_nonhermitian(M, a, b, name):
    """
    Report if `M` is not a hermitian matrix given the tolerances `a`, `b`.
    """
    from scipy.linalg import norm

    md = M - M.T.conj()

    nmd = norm(md, 1)
    tol = np.spacing(max(10**a, (10**b)*norm(M, 1)))
    if nmd > tol:
        print('matrix %s is not sufficiently Hermitian for a=%d, b=%d:'
              % (name, a, b))
        print('condition: %.e < %e' % (nmd, tol))