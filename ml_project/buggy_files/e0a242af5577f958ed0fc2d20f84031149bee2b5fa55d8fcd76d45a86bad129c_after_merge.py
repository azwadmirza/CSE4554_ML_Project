    def __call__(self, a, repeats):
        axis = self._axis
        a = astensor(a)
        if axis is None:
            a = ravel(a)

        ax = axis or 0

        if not isinstance(repeats, Integral):
            if not isinstance(repeats, Tensor):
                repeats = np.asarray(repeats)
                if repeats.size == 1:
                    repeats = int(repeats[0])
                    size = repeats * a.shape[axis or 0]
                elif a.shape[ax] == 1:
                    size = repeats = int(repeats.sum())
                else:
                    size = int(repeats.sum())
            else:
                size = np.nan
            if not isinstance(repeats, Integral):
                if repeats.ndim != 1:
                    raise ValueError('repeats should be 1-d tensor')
                broadcast_shape(repeats.shape, a.shape[ax: ax + 1])
        else:
            size = a.shape[axis or 0] * repeats

        shape = a.shape[:ax] + (size,) + a.shape[ax + 1:]
        self._dtype = a.dtype
        self._sparse = a.issparse()

        inputs = [a]
        if isinstance(repeats, Tensor):
            inputs.append(repeats)
        else:
            self._repeats = repeats

        return self.new_tensor(inputs, shape, order=TensorOrder.C_ORDER)