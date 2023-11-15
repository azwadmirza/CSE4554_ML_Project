    def get_data(self, element, ranges, style):
        if self._has_holes is None:
            draw_callbacks = any(isinstance(cb, (PolyDrawCallback, PolyEditCallback))
                                 for cb in self.callbacks)
            has_holes = (isinstance(element, Polygons) and not draw_callbacks)
            self._has_holes = has_holes
        else:
            has_holes = self._has_holes

        if not element.interface.multi:
            element = element.clone([element.data], datatype=type(element).datatype)

        if self.static_source:
            data = dict()
            xs = self.handles['cds'].data['xs']
        else:
            if has_holes:
                xs, ys = multi_polygons_data(element)
            else:
                xs, ys = (list(element.dimension_values(kd, expanded=False))
                          for kd in element.kdims)
            if self.invert_axes:
                xs, ys = ys, xs
            data = dict(xs=xs, ys=ys)
        mapping = dict(self._mapping)
        self._get_hover_data(data, element)

        color, fill_color = style.get('color'), style.get('fill_color')
        if (((isinstance(color, dim) and color.applies(element)) or color in element) or
            (isinstance(fill_color, dim) and fill_color.applies(element)) or fill_color in element):
            cdim = None
        elif None not in [element.level, self.color_index] and element.vdims:
            cdim = element.vdims[0]
        else:
            cidx = self.color_index+2 if isinstance(self.color_index, int) else self.color_index
            cdim = element.get_dimension(cidx)

        if cdim is None:
            return data, mapping, style

        ncontours = len(xs)
        dim_name = util.dimension_sanitizer(cdim.name)
        if element.level is not None:
            values = np.full(ncontours, float(element.level))
        else:
            values = element.dimension_values(cdim, expanded=False)
        data[dim_name] = values
        if cdim.name in ranges and 'factors' in ranges[cdim.name]:
            factors = ranges[cdim.name]['factors']
        else:
            factors = util.unique_array(np.concatenate(values)) if values.dtype.kind in 'SUO' else None
        cmapper = self._get_colormapper(cdim, element, ranges, style, factors)
        mapping[self._color_style] = {'field': dim_name, 'transform': cmapper}
        if self.show_legend:
            legend_prop = 'legend_field' if bokeh_version >= '1.3.5' else 'legend'
            mapping[legend_prop] = dim_name
        return data, mapping, style