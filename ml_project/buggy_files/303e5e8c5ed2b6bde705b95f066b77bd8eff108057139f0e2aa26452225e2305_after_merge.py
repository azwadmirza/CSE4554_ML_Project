    def get_data(self, element, ranges, style):
        data, mapping, style = HistogramPlot.get_data(self, element, ranges, style)
        color_dims = [d for d in self.adjoined.traverse(lambda x: x.handles.get('color_dim'))
                      if d is not None]
        dimension = color_dims[0] if color_dims else None
        cmapper = self._get_colormapper(dimension, element, {}, {})
        if cmapper and dimension in element.dimensions():
            if isinstance(dimension, dim):
                dim_name = dimension.dimension.name
                data[dim_name] = [] if self.static_source else dimension.apply(element)
            else:
                dim_name = dimension.name
                data[dim_name] = [] if self.static_source else element.dimension_values(dimension)
            mapping['fill_color'] = {'field': dim_name,
                                     'transform': cmapper}
        return (data, mapping, style)