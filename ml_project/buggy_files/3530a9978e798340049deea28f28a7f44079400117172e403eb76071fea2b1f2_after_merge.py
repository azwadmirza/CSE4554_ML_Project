    def _process(self, element, key=None):
        if isinstance(element, RGB):
            rgb = element.rgb
            data = self._preprocess_rgb(rgb)
        elif isinstance(element, Image):
            data = element.clone(datatype=['xarray']).data[element.vdims[0].name]
        else:
            raise ValueError('spreading can only be applied to Image or RGB Elements.')

        kwargs = {}
        array = self._apply_spreading(data)
        if isinstance(element, RGB):
            img = datashade.uint32_to_uint8(array.data)[::-1]
            new_data = {
                kd.name: rgb.dimension_values(kd, expanded=False)
                for kd in rgb.kdims
            }
            vdims = rgb.vdims+[rgb.alpha_dimension] if len(rgb.vdims) == 3 else rgb.vdims
            kwargs['vdims'] = vdims
            new_data[tuple(vd.name for vd in vdims)] = img
        else:
            new_data = array
        return element.clone(new_data, xdensity=element.xdensity,
                             ydensity=element.ydensity, **kwargs)