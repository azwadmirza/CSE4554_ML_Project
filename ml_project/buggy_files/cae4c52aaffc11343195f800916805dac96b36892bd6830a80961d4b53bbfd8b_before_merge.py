def calc_delta(Y, Ygrid, X, m):
    N = len(Y)
    fy = gaussian_kde(Y, bw_method='silverman')(Ygrid)
    abs_fy = np.abs(fy)
    xr = rankdata(X, method='ordinal')

    d_hat = 0
    for j in range(len(m) - 1):
        ix = np.where((xr > m[j]) & (xr <= m[j + 1]))[0]
        nm = len(ix)

        Y_ix = Y[ix]
        if not np.all(np.equal(Y_ix, Y_ix[0])):
            fyc = gaussian_kde(Y_ix, bw_method='silverman')(Ygrid)
            fy_ = np.abs(fy - fyc)
        else:
            fy_ = abs_fy
        
        d_hat += (nm / (2 * N)) * np.trapz(fy_, Ygrid)

    return d_hat