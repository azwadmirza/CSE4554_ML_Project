    def generic(self, args, kws):
        assert not kws
        ary, idx, val = args
        if not isinstance(ary, types.Buffer):
            return
        if not ary.mutable:
            raise TypeError("Cannot modify value of type %s" %(ary,))
        out = get_array_index_type(ary, idx)
        if out is None:
            return

        idx = out.index
        res = out.result
        if isinstance(res, types.Array):
            # Indexing produces an array
            if isinstance(val, types.Array):
                if not self.context.can_convert(val.dtype, res.dtype):
                    # DType conversion not possible
                    return
                else:
                    res = val
            elif isinstance(val, types.Sequence):
                if (res.ndim == 1 and
                    self.context.can_convert(val.dtype, res.dtype)):
                    # Allow assignement of sequence to 1d array
                    res = val
                else:
                    # NOTE: sequence-to-array broadcasting is unsupported
                    return
            else:
                # Allow scalar broadcasting
                if self.context.can_convert(val, res.dtype):
                    res = res.dtype
                else:
                    # Incompatible scalar type
                    return
        elif not isinstance(val, types.Array):
            # Single item assignment
            res = val
        else:
            return
        return signature(types.none, ary, idx, res)