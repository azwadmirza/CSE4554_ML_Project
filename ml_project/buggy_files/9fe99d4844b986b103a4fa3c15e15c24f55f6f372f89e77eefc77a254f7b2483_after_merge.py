def abcd_normalize(A=None, B=None, C=None, D=None):
    """Check state-space matrices and ensure they are rank-2.

    If enough information on the system is provided, that is, enough
    properly-shaped arrays are passed to the function, the missing ones
    are built from this information, ensuring the correct number of
    rows and columns. Otherwise a ValueError is raised.

    Parameters
    ----------
    A, B, C, D : array_like, optional
        State-space matrices. All of them are None (missing) by default.

    Returns
    -------
    A, B, C, D : array
        Properly shaped state-space matrices.

    Raises
    ------
    ValueError
        If not enough information on the system was provided.

    """
    A, B, C, D = map(_none_to_empty_2d, (A, B, C, D))
    A, B, C, D = map(atleast_2d, (A, B, C, D))

    MA, NA = A.shape
    MB, NB = B.shape
    MC, NC = C.shape
    MD, ND = D.shape

    p = (MA or MB or NC)
    q = (NB or ND)
    r = (MC or MD)

    if (p == 0) or (q == 0) or (r == 0):
        raise ValueError("Not enough information on the system.")

    A = _restore(A, (p, p))
    B = _restore(B, (p, q))
    C = _restore(C, (r, p))
    D = _restore(D, (r, q))

    return A, B, C, D