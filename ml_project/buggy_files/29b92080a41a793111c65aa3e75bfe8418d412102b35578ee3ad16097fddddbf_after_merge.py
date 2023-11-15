    def save_datasets(self, datasets, sector_id=None,
                      source_name=None, filename=None,
                      tile_count=(1, 1), tile_size=None,
                      lettered_grid=False, num_subtiles=None,
                      **kwargs):
        if sector_id is None:
            raise TypeError("Keyword 'sector_id' is required")

        def _area_id(area_def):
            return area_def.name + str(area_def.area_extent) + str(area_def.shape)
        # get all of the datasets stored by area
        area_datasets = {}
        for x in datasets:
            area_id = _area_id(x.attrs['area'])
            area, ds_list = area_datasets.setdefault(area_id, (x.attrs['area'], []))
            ds_list.append(x)

        output_filenames = []
        dtype = AWIPS_DATA_DTYPE
        fill_value = np.nan
        for area_id, (area_def, ds_list) in area_datasets.items():
            tile_gen = self._get_tile_generator(area_def, lettered_grid, sector_id, num_subtiles, tile_size, tile_count)
            for dataset in ds_list:
                pkwargs = {}
                ds_info = dataset.attrs.copy()
                LOG.info("Writing product %s to AWIPS SCMI NetCDF file", ds_info["name"])
                if isinstance(dataset, np.ma.MaskedArray):
                    data = dataset
                else:
                    mask = dataset.isnull()
                    data = np.ma.masked_array(dataset.values, mask=mask, copy=False)

                pkwargs['awips_info'] = self._get_awips_info(ds_info, source_name=source_name)
                pkwargs['attr_helper'] = AttributeHelper(ds_info)

                LOG.debug("Scaling %s data to fit in netcdf file...", ds_info["name"])
                bit_depth = ds_info.setdefault("bit_depth", 16)
                valid_min = ds_info.get('valid_min')
                if valid_min is None:
                    valid_min = np.nanmin(data)
                valid_max = ds_info.get('valid_max')
                if valid_max is None:
                    valid_max = np.nanmax(data)
                pkwargs['valid_min'] = valid_min
                pkwargs['valid_max'] = valid_max
                pkwargs['bit_depth'] = bit_depth

                LOG.debug("Using product valid min {} and valid max {}".format(valid_min, valid_max))
                fills, factor, offset = self._calc_factor_offset(
                    data=data,
                    bitdepth=bit_depth,
                    min=valid_min,
                    max=valid_max,
                    dtype=dtype,
                    flag_meanings='flag_meanings' in ds_info)
                pkwargs['fills'] = fills
                pkwargs['factor'] = factor
                pkwargs['offset'] = offset
                if 'flag_meanings' in ds_info:
                    pkwargs['data'] = data.astype(dtype)
                else:
                    pkwargs['data'] = data

                for (trow, tcol, tile_id, tmp_x, tmp_y), tmp_tile in tile_gen(data, fill_value=fill_value):
                    try:
                        fn = self.create_tile_output(
                            dataset, sector_id,
                            trow, tcol, tile_id, tmp_x, tmp_y, tmp_tile,
                            tile_gen.tile_count, tile_gen.image_shape,
                            tile_gen.mx, tile_gen.bx, tile_gen.my, tile_gen.by,
                            filename, **pkwargs)
                        if fn is None:
                            if lettered_grid:
                                LOG.warning("Data did not fit in to any lettered tile")
                            raise RuntimeError("No SCMI tiles were created")
                        output_filenames.append(fn)
                    except (RuntimeError, KeyError, AttributeError):
                        LOG.error("Could not create output for '%s'", ds_info['name'])
                        LOG.debug("Writer exception: ", exc_info=True)
                        raise

        return output_filenames[-1] if output_filenames else None