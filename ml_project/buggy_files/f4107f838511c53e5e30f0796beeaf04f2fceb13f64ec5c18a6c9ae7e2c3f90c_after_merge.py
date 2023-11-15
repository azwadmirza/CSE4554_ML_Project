    def __init__(self, kls, func, funcinvplus, funcinvminus, derivplus,
                 derivminus, *args, **kwargs):
        #print args
        #print kwargs

        self.func = func
        self.funcinvplus = funcinvplus
        self.funcinvminus = funcinvminus
        self.derivplus = derivplus
        self.derivminus = derivminus
        #explicit for self.__dict__.update(kwargs)
        #need to set numargs because inspection does not work
        self.numargs = kwargs.pop('numargs', 0)
        #print self.numargs
        name = kwargs.pop('name','transfdist')
        longname = kwargs.pop('longname','Non-linear transformed distribution')
        extradoc = kwargs.pop('extradoc',None)
        a = kwargs.pop('a', -np.inf) # attached to self in super
        b = kwargs.pop('b', np.inf)  # self.a, self.b would be overwritten
        self.shape = kwargs.pop('shape', False)
            #defines whether it is a `u` shaped or `hump' shaped
            #       transformation


        self.u_args, self.u_kwargs = get_u_argskwargs(**kwargs)
        self.kls = kls   #(self.u_args, self.u_kwargs)
                         # possible to freeze the underlying distribution

        super(TransfTwo_gen,self).__init__(a=a, b=b, name = name,
                                shapes = kls.shapes,
                                longname = longname, extradoc = extradoc)

        # add enough info for self.freeze() to be able to reconstruct the instance
        try:
            self._ctor_param.update(dict(kls=kls, func=func,
                    funcinvplus=funcinvplus, funcinvminus=funcinvminus,
                    derivplus=derivplus, derivminus=derivminus,
                    shape=self.shape))
        except AttributeError:
            # scipy < 0.14 does not have this, ignore and do nothing
            pass