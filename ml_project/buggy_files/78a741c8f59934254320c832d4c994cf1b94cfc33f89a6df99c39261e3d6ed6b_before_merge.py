    def save_datasets(self, datasets, filename, **kwargs):
        """Save all datasets to one or more files."""
        LOG.info('Saving datasets to NetCDF4/CF.')
        fields = []
        shapes = {}
        for dataset in datasets:
            if dataset.shape in shapes:
                domain = shapes[dataset.shape]
            else:
                lines, pixels = dataset.shape

                area = dataset.info.get('area')
                add_time = False
                try:
                    # Create a longitude auxiliary coordinate
                    lat = cf.AuxiliaryCoordinate(data=cf.Data(area.lats,
                                                              'degrees_north'))
                    lat.standard_name = 'latitude'

                    # Create a latitude auxiliary coordinate
                    lon = cf.AuxiliaryCoordinate(data=cf.Data(area.lons,
                                                              'degrees_east'))
                    lon.standard_name = 'longitude'
                    aux = [lat, lon]
                    add_time = True
                except AttributeError:
                    LOG.info('No longitude and latitude data to save.')
                    aux = None

                try:
                    grid_mapping = create_grid_mapping(area)
                    units = area.proj_dict.get('units', 'm')

                    line_coord = cf.DimensionCoordinate(
                        data=cf.Data(area.proj_y_coords, units))
                    line_coord.standard_name = "projection_y_coordinate"
                    pixel_coord = cf.DimensionCoordinate(
                        data=cf.Data(area.proj_x_coords, units))
                    pixel_coord.standard_name = "projection_x_coordinate"
                    add_time = True

                except (AttributeError, NotImplementedError):
                    LOG.info('No grid mapping to save.')
                    grid_mapping = None
                    line_coord = cf.DimensionCoordinate(
                        data=cf.Data(np.arange(lines), '1'))
                    line_coord.standard_name = "line"
                    pixel_coord = cf.DimensionCoordinate(
                        data=cf.Data(np.arange(pixels), '1'))
                    pixel_coord.standard_name = "pixel"

                start_time = cf.dt(dataset.info['start_time'])
                end_time = cf.dt(dataset.info['end_time'])
                middle_time = cf.dt((dataset.info['end_time'] -
                                     dataset.info['start_time']) / 2 +
                                    dataset.info['start_time'])
                # import ipdb
                # ipdb.set_trace()
                if add_time:
                    info = dataset.info
                    dataset = dataset[np.newaxis, :, :]
                    dataset.info = info

                    bounds = cf.CoordinateBounds(
                        data=cf.Data([start_time, end_time],
                                     cf.Units('days since 1970-1-1')))
                    time_coord = cf.DimensionCoordinate(properties=dict(standard_name='time'),
                                                        data=cf.Data(middle_time,
                                                                     cf.Units('days since 1970-1-1')),
                                                        bounds=bounds)
                    coords = [time_coord, line_coord, pixel_coord]
                else:
                    coords = [line_coord, pixel_coord]

                domain = cf.Domain(dim=coords,
                                   aux=aux,
                                   ref=grid_mapping)
                shapes[dataset.shape] = domain
            data = cf.Data(dataset, dataset.info.get('units', 'm'))

            # import ipdb
            # ipdb.set_trace()

            wanted_keys = ['standard_name', 'long_name']
            properties = {k: dataset.info[k]
                          for k in set(wanted_keys) & set(dataset.info.keys())}
            new_field = cf.Field(properties=properties,
                                 data=data,
                                 domain=domain)

            new_field._FillValue = dataset.fill_value
            try:
                new_field.valid_range = dataset.info['valid_range']
            except KeyError:
                new_field.valid_range = new_field.min(), new_field.max()
            new_field.Conventions = 'CF-1.7'
            fields.append(new_field)

        fields[0].history = ("Created by pytroll/satpy on " +
                             str(datetime.utcnow()))

        flist = cf.FieldList(fields)

        cf.write(flist, filename, fmt='NETCDF4', compress=6)