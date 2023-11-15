def makeYbus(baseMVA, bus, branch):
    """Builds the bus admittance matrix and branch admittance matrices.

    Returns the full bus admittance matrix (i.e. for all buses) and the
    matrices C{Yf} and C{Yt} which, when multiplied by a complex voltage
    vector, yield the vector currents injected into each line from the
    "from" and "to" buses respectively of each line. Does appropriate
    conversions to p.u.

    @see: L{makeSbus}

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln

    modified by Florian Schaefer (to use numba) (florian.schaefer@uni-kassel.de)
    """
    ## constants
    nb = bus.shape[0]  ## number of buses
    nl = branch.shape[0]  ## number of lines

    ## for each branch, compute the elements of the branch admittance matrix where
    ##
    ##      | If |   | Yff  Yft |   | Vf |
    ##      |    | = |          | * |    |
    ##      | It |   | Ytf  Ytt |   | Vt |
    ##
    Ytt, Yff, Yft, Ytf = branch_vectors(branch, nl)

    ## compute shunt admittance
    ## if Psh is the real power consumed by the shunt at V = 1.0 p.u.
    ## and Qsh is the reactive power injected by the shunt at V = 1.0 p.u.
    ## then Psh - j Qsh = V * conj(Ysh * V) = conj(Ysh) = Gs - j Bs,
    ## i.e. Ysh = Psh + j Qsh, so ...
    ## vector of shunt admittances
    Ysh = (bus[:, GS] + 1j * bus[:, BS]) / baseMVA

    ## build connection matrices
    f = np.real(branch[:, F_BUS]).astype(int)  ## list of "from" buses
    t = np.real(branch[:, T_BUS]).astype(int)  ## list of "to" buses

    ## build Yf and Yt such that Yf * V is the vector of complex branch currents injected
    ## at each branch's "from" bus, and Yt is the same for the "to" bus end
    i = np.hstack([np.arange(nl), np.arange(nl)])  ## double set of row indices

    Yf_x = np.hstack([Yff, Yft])
    Yt_x = np.hstack([Ytf, Ytt])
    col_Y = np.hstack([f, t])

    Yf = coo_matrix((Yf_x, (i, col_Y)), (nl, nb)).tocsr()
    Yt = coo_matrix((Yt_x, (i, col_Y)), (nl, nb)).tocsr()
    Yx, Yj, Yp, nnz = gen_Ybus(Yf_x, Yt_x, Ysh, col_Y, f, t, np.argsort(f), np.argsort(t), nb, nl,
                               np.arange(nl, dtype=np.int64))
    Ybus = csr_matrix((np.resize(Yx, nnz), np.resize(Yj, nnz), Yp), (nb, nb))
    return Ybus, Yf, Yt