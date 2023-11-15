    def entropy(self, *args, **kwds):
        args, loc, _ = self._parse_args(*args, **kwds)
        loc = asarray(loc)
        args = list(map(asarray,args))
        cond0 = self._argcheck(*args) & (loc == loc)
        output = zeros(shape(cond0),'d')
        place(output,(1-cond0),self.badvalue)
        goodargs = argsreduce(cond0, *args)
        place(output,cond0,self.vecentropy(*goodargs))
        return output