    def nnlf(self, theta, x):
        ''' Return negative loglikelihood function, 
        i.e., - sum (log pdf(x, theta),axis=0)
           where theta are the parameters (including loc and scale)
        '''
        try:
            loc = theta[-2]
            scale = theta[-1]
            args = tuple(theta[:-2])
        except IndexError:
            raise ValueError("Not enough input arguments.")
        if not self._argcheck(*args) or scale <= 0:
            return inf
        x = asarray((x-loc) / scale)
        cond0 = (x <= self.a) | (self.b <= x )
        if (any(cond0)):
            # old call: return inf
            goodargs = argsreduce(1 - cond0, *((x,)))
            goodargs = tuple(goodargs + list(args))
            N = len(x)
            Nbad = sum(cond0)
            xmax = floatinfo.machar.xmax
            return self._nnlf(*goodargs) + N * log(scale) + Nbad * 100.0 * log(xmax)
        else:
            N = len(x)
            return self._nnlf(x, *args) + N*log(scale)