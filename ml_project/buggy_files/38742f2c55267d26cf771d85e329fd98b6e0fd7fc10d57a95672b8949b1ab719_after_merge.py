    def __init__(self, roots, weights=None, hn=1.0, kn=1.0, wfunc=None,
                 limits=None, monic=False, eval_func=None):
        np.poly1d.__init__(self, roots, r=1)
        equiv_weights = [weights[k] / wfunc(roots[k]) for
                         k in range(len(roots))]
        self.__dict__['weights'] = np.array(list(zip(roots,
                                                     weights, equiv_weights)))
        self.__dict__['weight_func'] = wfunc
        self.__dict__['limits'] = limits
        mu = sqrt(hn)
        if monic:
            evf = eval_func
            if evf:
                eval_func = lambda x: evf(x) / kn
            mu = mu / abs(kn)
            kn = 1.0
        self.__dict__['normcoef'] = mu
        self.__dict__['coeffs'] *= float(kn)

        # Note: eval_func will be discarded on arithmetic
        self.__dict__['_eval_func'] = eval_func