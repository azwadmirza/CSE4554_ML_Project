    def _call(self, x1, x2, out=None, where=None):
        # if x1 or x2 is scalar, and out is none, to constant
        if (np.isscalar(x1) or np.isscalar(x2)) and not out and not where:
            return self.to_constant(x1, x2)

        x1, x2, out, where = self._process_inputs(x1, x2, out, where)
        # check broadcast
        shape = broadcast_shape(x1.shape, x2.shape)

        t = self.new_tensor([x1, x2, out, where], shape)

        if out is None:
            return t

        check_out_param(out, t, getattr(self, '_casting'))
        out_shape, out_dtype = out.shape, out.dtype

        # if `out` is specified, use out's dtype and shape
        if t.shape != out_shape:
            t = self.new_tensor([x1, x2, out, where], out_shape)
        setattr(self, '_dtype', out_dtype)

        out.data = t.data
        return out