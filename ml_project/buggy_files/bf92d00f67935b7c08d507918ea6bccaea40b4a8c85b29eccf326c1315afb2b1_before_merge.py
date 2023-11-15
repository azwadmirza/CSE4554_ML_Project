    def _build(self):
        """Build the plot by calling needed plotting methods as necessary."""
        lon, lat, data = self.plotdata

        # Use the cartopy map projection to transform station locations to the map and
        # then refine the number of stations plotted by setting a radius
        if self.parent._proj_obj == ccrs.PlateCarree():
            scale = 1.
        else:
            scale = 100000.
        point_locs = self.parent._proj_obj.transform_points(ccrs.PlateCarree(), lon, lat)
        subset = reduce_point_density(point_locs, self.reduce_points * scale)

        self.handle = StationPlot(self.parent.ax, lon[subset], lat[subset], clip_on=True,
                                  transform=ccrs.PlateCarree(), fontsize=10)

        for i, ob_type in enumerate(self.fields):
            field_kwargs = {}
            if len(self.locations) > 1:
                location = self.locations[i]
            else:
                location = self.locations[0]
            if len(self.colors) > 1:
                field_kwargs['color'] = self.colors[i]
            else:
                field_kwargs['color'] = self.colors[0]
            if len(self.formats) > 1:
                field_kwargs['formatter'] = self.formats[i]
            else:
                field_kwargs['formatter'] = self.formats[0]
            if len(self.plot_units) > 1:
                field_kwargs['plot_units'] = self.plot_units[i]
            else:
                field_kwargs['plot_units'] = self.plot_units[0]
            if hasattr(self.data, 'units') and (field_kwargs['plot_units'] is not None):
                parameter = data[ob_type][subset].values * units(self.data.units[ob_type])
            else:
                parameter = data[ob_type][subset]
            if field_kwargs['formatter'] is not None:
                mapper = getattr(wx_symbols, str(field_kwargs['formatter']), None)
                if mapper is not None:
                    field_kwargs.pop('formatter')
                    self.handle.plot_symbol(location, parameter,
                                            mapper, **field_kwargs)
                else:
                    if self.formats[i] == 'text':
                        self.handle.plot_text(location, data[ob_type][subset],
                                              color=field_kwargs['color'])
                    else:
                        self.handle.plot_parameter(location, data[ob_type][subset],
                                                   **field_kwargs)
            else:
                field_kwargs.pop('formatter')
                self.handle.plot_parameter(location, parameter, **field_kwargs)

        if self.vector_field[0] is not None:
            vector_kwargs = {}
            vector_kwargs['color'] = self.vector_field_color
            vector_kwargs['plot_units'] = self.vector_plot_units
            if hasattr(self.data, 'units') and (vector_kwargs['plot_units'] is not None):
                u = (data[self.vector_field[0]][subset].values
                     * units(self.data.units[self.vector_field[0]]))
                v = (data[self.vector_field[1]][subset].values
                     * units(self.data.units[self.vector_field[1]]))
            else:
                vector_kwargs.pop('plot_units')
                u = data[self.vector_field[0]][subset]
                v = data[self.vector_field[1]][subset]
            if self.vector_field_length is not None:
                vector_kwargs['length'] = self.vector_field_length
            self.handle.plot_barb(u, v, **vector_kwargs)