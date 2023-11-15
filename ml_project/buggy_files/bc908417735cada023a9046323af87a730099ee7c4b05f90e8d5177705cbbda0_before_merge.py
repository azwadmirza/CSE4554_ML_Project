    def call(cls, func, args, kws, loc, vararg=None):
        assert isinstance(func, (Var, Intrinsic))
        assert isinstance(loc, Loc)
        op = 'call'
        return cls(op=op, loc=loc, func=func, args=args, kws=kws,
                   vararg=vararg)