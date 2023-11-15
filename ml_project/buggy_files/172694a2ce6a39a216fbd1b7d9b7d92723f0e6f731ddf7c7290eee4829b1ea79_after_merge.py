    def entropy(self, *args, **kwds):
        args, loc, _ = self._parse_args(*args, **kwds)
        loc = asarray(loc)
        args = list(map(asarray,args))
        cond0 = self._argcheck(*args) & (loc == loc)
        output = zeros(shape(cond0),'d')
        place(output,(1-cond0),self.badvalue)
        goodargs = argsreduce(cond0, *args)
        # np.vectorize doesn't work when numargs == 0 in numpy 1.5.1
        if self.numargs == 0:
            place(output, cond0, self._entropy())
        else:
            place(output, cond0, self.vecentropy(*goodargs))

        return output