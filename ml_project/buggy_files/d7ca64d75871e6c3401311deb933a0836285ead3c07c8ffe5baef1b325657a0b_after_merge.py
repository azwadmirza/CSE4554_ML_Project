    def __str__(self):
        """
        String representation.

        """
        if masked_print_option.enabled():
            f = masked_print_option
            if self is masked:
                return str(f)
            m = self._mask
            if m is nomask:
                res = self._data
            else:
                if m.shape == ():
                    if m.dtype.names:
                        m = m.view((bool, len(m.dtype)))
                        if m.any():
                            return str(tuple((f if _m else _d) for _d, _m in
                                             zip(self._data.tolist(), m)))
                        else:
                            return str(self._data)
                    elif m:
                        return str(f)
                    else:
                        return str(self._data)
                # convert to object array to make filled work
                names = self.dtype.names
                if names is None:
                    data = self._data
                    mask = m
                    nval = 50
                    # For big arrays, to avoid a costly conversion to the
                    # object dtype, extract the corners before the conversion.
                    for axis in range(self.ndim):
                        if data.shape[axis] > 2 * nval:
                            arr = np.split(data, (nval, -nval), axis=axis)
                            data = np.concatenate((arr[0], arr[2]), axis=axis)
                            arr = np.split(mask, (nval, -nval), axis=axis)
                            mask = np.concatenate((arr[0], arr[2]), axis=axis)
                    res = data.astype("O")
                    res.view(ndarray)[mask] = f
                else:
                    rdtype = _recursive_make_descr(self.dtype, "O")
                    res = self._data.astype(rdtype)
                    _recursive_printoption(res, m, f)
        else:
            res = self.filled(self.fill_value)
        return str(res)