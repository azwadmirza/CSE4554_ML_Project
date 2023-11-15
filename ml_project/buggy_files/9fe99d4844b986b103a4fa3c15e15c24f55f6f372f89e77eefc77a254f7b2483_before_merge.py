def abcd_normalize(A=None, B=None, C=None, D=None):
    """Check state-space matrices and ensure they are rank-2.

    """
    A, B, C, D = map(_none_to_empty, (A, B, C, D))
    A, B, C, D = map(atleast_2d, (A, B, C, D))

    if ((len(A.shape) > 2) or (len(B.shape) > 2) or
        (len(C.shape) > 2) or (len(D.shape) > 2)):
        raise ValueError("A, B, C, D arrays can be no larger than rank-2.")

    MA, NA = A.shape
    MB, NB = B.shape
    MC, NC = C.shape
    MD, ND = D.shape

    if (MC == 0) and (NC == 0) and (MD != 0) and (NA != 0):
        MC, NC = MD, NA
        C = zeros((MC, NC))
    if (MB == 0) and (NB == 0) and (MA != 0) and (ND != 0):
        MB, NB = MA, ND
        B = zeros((MB, NB))
    if (MD == 0) and (ND == 0) and (MC != 0) and (NB != 0):
        MD, ND = MC, NB
        D = zeros((MD, ND))
    if (MA == 0) and (NA == 0) and (MB != 0) and (NC != 0):
        MA, NA = MB, NC
        A = zeros((MA, NA))

    if MA != NA:
        raise ValueError("A must be square.")
    if MA != MB:
        raise ValueError("A and B must have the same number of rows.")
    if NA != NC:
        raise ValueError("A and C must have the same number of columns.")
    if MD != MC:
        raise ValueError("C and D must have the same number of rows.")
    if ND != NB:
        raise ValueError("B and D must have the same number of columns.")

    return A, B, C, D