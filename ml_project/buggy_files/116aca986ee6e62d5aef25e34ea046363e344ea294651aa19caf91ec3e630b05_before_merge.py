        def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
            func = getattr(ufunc, method)
            if 'out' in kwargs:
                out_orig = kwargs.pop('out')
                out = np.asarray(out_orig[0])
            else:
                out = None
            if len(inputs) == 1:
                _, inp, u = get_inp_u_unary(ufunc, inputs)
                out_arr = func(np.asarray(inp), out=out, **kwargs)
                if ufunc in (multiply, divide) and method == 'reduce':
                    power_sign = POWER_SIGN_MAPPING[ufunc]
                    if 'axis' in kwargs and kwargs['axis'] is not None:
                        unit = u**(power_sign*inp.shape[kwargs['axis']])
                    else:
                        unit = u**(power_sign*inp.size)
                else:
                    unit = self._ufunc_registry[ufunc](u)
                ret_class = type(self)
            elif len(inputs) == 2:
                unit_operator = self._ufunc_registry[ufunc]
                inps, units, ret_class = get_inp_u_binary(ufunc, inputs)
                if unit_operator in (comparison_unit, arctan2_unit):
                    inps, units = handle_comparison_units(
                        inps, units, ufunc, ret_class)
                elif unit_operator is preserve_units:
                    inps, units = handle_preserve_units(
                         inps, units, ufunc, ret_class)
                unit = unit_operator(*units)
                out_arr = func(np.asarray(inps[0]), np.asarray(inps[1]),
                               out=out, **kwargs)
                if unit_operator in (multiply_units, divide_units):
                    out, out_arr, unit = handle_multiply_divide_units(
                        unit, units, out, out_arr)
            else:
                if ufunc is clip:
                    inp = []
                    for i in inputs:
                        if isinstance(i, YTArray):
                            inp.append(i.to(inputs[0].units).view(np.ndarray))
                        elif iterable(i):
                            inp.append(np.asarray(i))
                        else:
                            inp.append(i)
                    if out is not None:
                        _out = out.view(np.ndarray)
                    else:
                        _out = None
                    out_arr = ufunc(*inp, out=_out)
                    unit = inputs[0].units
                    ret_class = type(inputs[0])
                    # This was added after unyt was spun out, but is not presently used:
                    # mul = 1
                else:
                    raise RuntimeError(
                        "Support for the %s ufunc with %i inputs has not been "
                        "added to unyt_array." % (str(ufunc), len(inputs))
                    )
            if unit is None:
                out_arr = np.array(out_arr, copy=False)
            elif ufunc in (modf, divmod_):
                out_arr = tuple((ret_class(o, unit) for o in out_arr))
            elif out_arr.size == 1:
                out_arr = YTQuantity(np.asarray(out_arr), unit)
            else:
                if ret_class is YTQuantity:
                    # This happens if you do ndarray * YTQuantity. Explicitly
                    # casting to YTArray avoids creating a YTQuantity with
                    # size > 1
                    out_arr = YTArray(np.asarray(out_arr), unit)
                else:
                    out_arr = ret_class(np.asarray(out_arr), unit)
            if out is not None:
                out_orig[0].flat[:] = out.flat[:]
                if isinstance(out_orig[0], YTArray):
                    out_orig[0].units = unit
            return out_arr