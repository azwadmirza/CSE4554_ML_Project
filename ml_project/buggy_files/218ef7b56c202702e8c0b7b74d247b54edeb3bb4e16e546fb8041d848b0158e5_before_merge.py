    def fit(self, data, *args, **kwds):
        floc = kwds.get('floc', None)
        if floc is None:
            # loc is not fixed.  Use the default fit method.
            return super(lognorm_gen, self).fit(data, *args, **kwds)

        f0 = (kwds.get('f0', None) or kwds.get('fs', None) or
              kwds.get('fix_s', None))
        fscale = kwds.get('fscale', None)

        if len(args) > 1:
            raise TypeError("Too many input arguments.")
        for name in ['f0', 'fs', 'fix_s', 'floc', 'fscale', 'loc', 'scale',
                     'optimizer']:
            kwds.pop(name, None)
        if kwds:
            raise TypeError("Unknown arguments: %s." % kwds)

        # Special case: loc is fixed.  Use the maximum likelihood formulas
        # instead of the numerical solver.

        if f0 is not None and fscale is not None:
            # This check is for consistency with `rv_continuous.fit`.
            raise ValueError("All parameters fixed. There is nothing to "
                             "optimize.")

        data = np.asarray(data)
        floc = float(floc)
        if floc != 0:
            # Shifting the data by floc. Don't do the subtraction in-place,
            # because `data` might be a view of the input array.
            data = data - floc
        if np.any(data <= 0):
            raise FitDataError("lognorm", lower=floc, upper=np.inf)
        lndata = np.log(data)

        # Three cases to handle:
        # * shape and scale both free
        # * shape fixed, scale free
        # * shape free, scale fixed

        if fscale is None:
            # scale is free.
            scale = np.exp(lndata.mean())
            if f0 is None:
                # shape is free.
                shape = lndata.std()
            else:
                # shape is fixed.
                shape = float(f0)
        else:
            # scale is fixed, shape is free
            scale = float(fscale)
            shape = np.sqrt(((lndata - np.log(scale))**2).mean())

        return shape, floc, scale