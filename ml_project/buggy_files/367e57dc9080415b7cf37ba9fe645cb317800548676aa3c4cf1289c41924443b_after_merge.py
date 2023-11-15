    def _call(self, x1, x2, out=None, where=None):
        # check tensor ufunc, if x1 or x2 is not a tensor, e.g. Mars DataFrame
        # which implements tensor ufunc, will delegate the computation
        # to it if possible
        ret = self._call_tensor_ufunc(x1, x2, out=out, where=where)
        if ret is not None:
            return ret

        x1, x2, out, where = self._process_inputs(x1, x2, out, where)
        # check broadcast
        x1_shape = () if np.isscalar(x1) else x1.shape
        x2_shape = () if np.isscalar(x2) else x2.shape
        shape = broadcast_shape(x1_shape, x2_shape)
        order = self._calc_order(x1, x2, out)

        inputs = filter_inputs([x1, x2, out, where])
        t = self.new_tensor(inputs, shape, order=order)

        if out is None:
            return t

        check_out_param(out, t, getattr(self, '_casting'))
        out_shape, out_dtype = out.shape, out.dtype

        # if `out` is specified, use out's dtype and shape
        if t.shape != out_shape:
            t = self.new_tensor(inputs, out_shape, order=order)
        setattr(self, '_dtype', out_dtype)

        out.data = t.data
        return out