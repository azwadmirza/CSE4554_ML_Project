    def entropy(self, *args, **kwds):
        """
        Differential entropy of the RV.

        Parameters
        ----------
        arg1, arg2, arg3,... : array_like
            The shape parameter(s) for the distribution (see docstring of the
            instance object for more information).
        loc : array_like, optional
            Location parameter (default=0).
        scale : array_like, optional
            Scale parameter (default=1).

        """
        args, loc, scale = self._parse_args(*args, **kwds)
        args = tuple(map(asarray,args))
        cond0 = self._argcheck(*args) & (scale > 0) & (loc == loc)
        output = zeros(shape(cond0),'d')
        place(output,(1-cond0),self.badvalue)
        goodargs = argsreduce(cond0, *args)
        # np.vectorize doesn't work when numargs == 0 in numpy 1.5.1
        if self.numargs == 0:
            place(output,cond0,self._entropy()+log(scale))
        else:
            place(output,cond0,self.vecentropy(*goodargs)+log(scale))

        return output