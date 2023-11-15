    def _on_data_change(self):
        data = self.layer._data_view
        dtype = np.dtype(data.dtype)
        if dtype not in texture_dtypes:
            try:
                dtype = dict(i=np.int16, f=np.float64)[dtype.kind]
            except KeyError:  # not an int or float
                raise TypeError(
                    f'type {dtype} not allowed for texture; must be one of {set(texture_dtypes)}'
                )
            data = data.astype(dtype)

        self.node._need_colortransform_update = True
        self.node.set_data(data)
        self.node.update()