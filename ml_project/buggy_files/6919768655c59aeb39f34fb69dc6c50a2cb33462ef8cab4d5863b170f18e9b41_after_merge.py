    def _on_data_change(self):
        data = self.layer._data_view
        dtype = np.dtype(data.dtype)
        if dtype not in texture_dtypes:
            try:
                dtype = dict(i=np.int16, f=np.float32)[dtype.kind]
            except KeyError:  # not an int or float
                raise TypeError(
                    f'type {dtype} not allowed for texture; must be one of {set(texture_dtypes)}'
                )
            data = data.astype(dtype)

        if self.layer.dims.ndisplay == 3:
            self.node.set_data(data, clim=self.layer.contrast_limits)
        else:
            self.node._need_colortransform_update = True
            self.node.set_data(data)
        self.node.update()