    def get_data(self, element, ranges, style):
        data, mapping, style = HistogramPlot.get_data(self, element, ranges, style)
        color_dims = [d for d in self.adjoined.traverse(lambda x: x.handles.get('color_dim'))
                      if d is not None]
        dim = color_dims[0] if color_dims else None
        cmapper = self._get_colormapper(dim, element, {}, {})
        if cmapper and dim in element.dimensions():
            data[dim.name] = [] if self.static_source else element.dimension_values(dim)
            mapping['fill_color'] = {'field': dim.name,
                                     'transform': cmapper}
        return (data, mapping, style)