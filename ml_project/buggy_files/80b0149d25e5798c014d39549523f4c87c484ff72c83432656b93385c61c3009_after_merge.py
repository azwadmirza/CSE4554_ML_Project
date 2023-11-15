    def __getitem__(self, key):
        # handle matrix builder syntax
        if isinstance(key, str):
            frame = sys._getframe().f_back
            mymat = matrixlib.bmat(key, frame.f_globals, frame.f_locals)
            return mymat

        if not isinstance(key, tuple):
            key = (key,)

        # copy attributes, since they can be overriden in the first argument
        trans1d = self.trans1d
        ndmin = self.ndmin
        matrix = self.matrix
        axis = self.axis

        objs = []
        scalars = []
        arraytypes = []
        scalartypes = []

        for k in range(len(key)):
            scalar = False
            if isinstance(key[k], slice):
                step = key[k].step
                start = key[k].start
                stop = key[k].stop
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                if isinstance(step, complex):
                    size = int(abs(step))
                    newobj = function_base.linspace(start, stop, num=size)
                else:
                    newobj = _nx.arange(start, stop, step)
                if ndmin > 1:
                    newobj = array(newobj, copy=False, ndmin=ndmin)
                    if trans1d != -1:
                        newobj = newobj.swapaxes(-1, trans1d)
            elif isinstance(key[k], str):
                if k != 0:
                    raise ValueError("special directives must be the "
                            "first entry.")
                key0 = key[0]
                if key0 in 'rc':
                    matrix = True
                    col = (key0 == 'c')
                    continue
                if ',' in key0:
                    vec = key0.split(',')
                    try:
                        axis, ndmin = [int(x) for x in vec[:2]]
                        if len(vec) == 3:
                            trans1d = int(vec[2])
                        continue
                    except:
                        raise ValueError("unknown special directive")
                try:
                    axis = int(key[k])
                    continue
                except (ValueError, TypeError):
                    raise ValueError("unknown special directive")
            elif type(key[k]) in ScalarType:
                newobj = array(key[k], ndmin=ndmin)
                scalars.append(k)
                scalar = True
                scalartypes.append(newobj.dtype)
            else:
                newobj = key[k]
                if ndmin > 1:
                    tempobj = array(newobj, copy=False, subok=True)
                    newobj = array(newobj, copy=False, subok=True,
                                   ndmin=ndmin)
                    if trans1d != -1 and tempobj.ndim < ndmin:
                        k2 = ndmin-tempobj.ndim
                        if (trans1d < 0):
                            trans1d += k2 + 1
                        defaxes = list(range(ndmin))
                        k1 = trans1d
                        axes = defaxes[:k1] + defaxes[k2:] + \
                               defaxes[k1:k2]
                        newobj = newobj.transpose(axes)
                    del tempobj
            objs.append(newobj)
            if not scalar and isinstance(newobj, _nx.ndarray):
                arraytypes.append(newobj.dtype)

        # Ensure that scalars won't up-cast unless warranted
        final_dtype = find_common_type(arraytypes, scalartypes)
        if final_dtype is not None:
            for k in scalars:
                objs[k] = objs[k].astype(final_dtype)

        res = self.concatenate(tuple(objs), axis=axis)

        if matrix:
            oldndim = res.ndim
            res = makemat(res)
            if oldndim == 1 and col:
                res = res.T
        return res