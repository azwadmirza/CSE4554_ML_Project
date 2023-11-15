    def apply_filter(self, x, axis=-1, mode='constant', cval=0):
        """Apply the prepared filter to the specified axis of a N-D signal x"""
        output_len = _output_len(len(self._h_trans_flip), x.shape[axis],
                                 self._up, self._down)
        # Explicit use of np.int64 for output_shape dtype avoids OverflowError
        # when allocating large array on platforms where np.int_ is 32 bits
        output_shape = np.asarray(x.shape, dtype=np.int64)
        output_shape[axis] = output_len
        out = np.zeros(output_shape, dtype=self._output_type, order='C')
        axis = axis % x.ndim
        mode = _check_mode(mode)
        _apply(np.asarray(x, self._output_type),
               self._h_trans_flip, out,
               self._up, self._down, axis, mode, cval)
        return out