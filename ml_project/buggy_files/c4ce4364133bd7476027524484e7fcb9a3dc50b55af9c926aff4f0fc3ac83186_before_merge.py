    def nnlf(self, theta, x):
        # - sum (log pdf(x, theta),axis=0)
        #   where theta are the parameters (including loc and scale)
        #
        try:
            loc = theta[-2]
            scale = theta[-1]
            args = tuple(theta[:-2])
        except IndexError:
            raise ValueError("Not enough input arguments.")
        if not self._argcheck(*args) or scale <= 0:
            return inf
        x = asarray((x-loc) / scale)
        cond0 = (x <= self.a) | (x >= self.b)
        if (any(cond0)):
            return inf
        else:
            N = len(x)
            return self._nnlf(x, *args) + N*log(scale)