    def get_data(self, element, ranges, style):
        cdim = element.get_dimension(self.color_index)

        with abbreviated_exception():
            style = self._apply_transforms(element, ranges, style)

        scalar = element.interface.isunique(element, cdim, per_geom=True) if cdim else False
        style_mapping = any(isinstance(v, util.arraylike_types) and not (k == 'c' and scalar)
                         for k, v in style.items())
        dims = element.kdims
        xdim, ydim = dims
        generic_dt_format = Dimension.type_formatters[np.datetime64]
        paths, cvals, dims = [], [], {}
        for path in element.split(datatype='columns'):
            xarr, yarr = path[xdim.name], path[ydim.name]
            if util.isdatetime(xarr):
                dt_format = Dimension.type_formatters.get(type(xarr[0]), generic_dt_format)
                xarr = date2num(xarr)
                dims[0] = xdim(value_format=DateFormatter(dt_format))
            if util.isdatetime(yarr):
                dt_format = Dimension.type_formatters.get(type(yarr[0]), generic_dt_format)
                yarr = date2num(yarr)
                dims[1] = ydim(value_format=DateFormatter(dt_format))
            arr = np.column_stack([xarr, yarr])
            if not (self.color_index is not None or style_mapping):
                paths.append(arr)
                continue
            length = len(xarr)
            for (s1, s2) in zip(range(length-1), range(1, length+1)):
                if cdim:
                    cvals.append(path[cdim.name])
                paths.append(arr[s1:s2+1])
        if self.invert_axes:
            paths = [p[::-1] for p in paths]
        if not (self.color_index or style_mapping):
            if cdim:
                style['array'] = style.pop('c')
                style['clim'] = style.pop('vmin', None), style.pop('vmax', None)
            return (paths,), style, {'dimensions': dims}
        if cdim:
            self._norm_kwargs(element, ranges, style, cdim)
            style['array'] = np.array(cvals)
        if 'c' in style:
            style['array'] = style.pop('c')
        if 'vmin' in style:
            style['clim'] = style.pop('vmin', None), style.pop('vmax', None)
        return (paths,), style, {'dimensions': dims}