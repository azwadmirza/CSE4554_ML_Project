    def _winsorize1D(a, low_limit, up_limit, low_include, up_include):
        n = a.count()
        idx = a.argsort()
        if low_limit:
            if low_include:
                lowidx = int(low_limit * n)
            else:
                lowidx = np.round(low_limit * n)
            a[idx[:lowidx]] = a[idx[lowidx]]
        if up_limit is not None:
            if up_include:
                upidx = n - int(n * up_limit)
            else:
                upidx = n - np.round(n * up_limit)
            a[idx[upidx:]] = a[idx[upidx - 1]]
        return a