    def __init__(self, a=0, b=inf, name=None, badvalue=None,
                 moment_tol=1e-8, values=None, inc=1, longname=None,
                 shapes=None, extradoc=None, seed=None):

        super(rv_discrete, self).__init__(seed)

        if values is None:
            raise ValueError("rv_sample.__init__(..., values=None,...)")

        # cf generic freeze
        self._ctor_param = dict(
            a=a, b=b, name=name, badvalue=badvalue,
            moment_tol=moment_tol, values=values, inc=inc,
            longname=longname, shapes=shapes, extradoc=extradoc, seed=seed)

        if badvalue is None:
            badvalue = nan
        self.badvalue = badvalue
        self.moment_tol = moment_tol
        self.inc = inc
        self.shapes = shapes
        self.vecentropy = self._entropy

        xk, pk = values

        if np.shape(xk) != np.shape(pk):
            raise ValueError("xk and pk must have the same shape.")
        if not np.allclose(np.sum(pk), 1):
            raise ValueError("The sum of provided pk is not 1.")

        indx = np.argsort(np.ravel(xk))
        self.xk = np.take(np.ravel(xk), indx, 0)
        self.pk = np.take(np.ravel(pk), indx, 0)
        self.a = self.xk[0]
        self.b = self.xk[-1]
        self.qvals = np.cumsum(self.pk, axis=0)

        self.shapes = ' '   # bypass inspection
        self._construct_argparser(meths_to_inspect=[self._pmf],
                                  locscale_in='loc=0',
                                  # scale=1 for discrete RVs
                                  locscale_out='loc, 1')

        self._construct_docstrings(name, longname, extradoc)