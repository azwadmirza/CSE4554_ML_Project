    def create_tile_output(self, dataset, sector_id,
                           trow, tcol, tile_id, tmp_x, tmp_y, tmp_tile,
                           tile_count, image_shape,
                           mx, bx, my, by,
                           filename,
                           awips_info, attr_helper,
                           fills, factor, offset, valid_min, valid_max, bit_depth, **kwargs):
        # Create the netcdf file
        ds_info = dataset.info
        area_def = ds_info['area']
        created_files = []
        try:
            if filename is None:
                # format the filename
                of_kwargs = ds_info.copy()
                of_kwargs["start_time"] += timedelta(minutes=int(os.environ.get("DEBUG_TIME_SHIFT", 0)))
                output_filename = self.get_filename(
                    area_id=area_def.area_id,
                    rows=area_def.y_size,
                    columns=area_def.x_size,
                    source_name=awips_info['source_name'],
                    sector_id=sector_id,
                    tile_id=tile_id,
                    **of_kwargs
                )
            else:
                output_filename = filename
            if os.path.isfile(output_filename):
                if not self.overwrite_existing:
                    LOG.error("AWIPS file already exists: %s", output_filename)
                    raise RuntimeError("AWIPS file already exists: %s" % (output_filename,))
                else:
                    LOG.warning("AWIPS file already exists, will overwrite: %s", output_filename)
            created_files.append(output_filename)

            LOG.info("Writing tile '%s' to '%s'", tile_id, output_filename)

            nc = NetCDFWriter(output_filename, helper=attr_helper,
                              compress=self.compress)
            LOG.debug("Creating dimensions...")
            nc.create_dimensions(tmp_tile.shape[0], tmp_tile.shape[1])
            LOG.debug("Creating variables...")
            nc.create_variables(bit_depth, fills[0], factor, offset)
            LOG.debug("Creating global attributes...")
            nc.set_global_attrs(awips_info['physical_element'],
                                awips_info['awips_id'], sector_id,
                                awips_info['creating_entity'],
                                tile_count, image_shape,
                                trow, tcol, tmp_tile.shape[0], tmp_tile.shape[1])
            LOG.debug("Creating projection attributes...")
            nc.set_projection_attrs(area_def.area_id, area_def.proj_dict)
            LOG.debug("Writing image data...")
            np.clip(tmp_tile, valid_min, valid_max, out=tmp_tile)
            nc.set_image_data(tmp_tile, fills[0])
            LOG.debug("Writing X/Y navigation data...")
            nc.set_fgf(tmp_x, mx, bx,
                       tmp_y, my, by, units='meters')
            nc.close()

            if self.fix_awips:
                self._fix_awips_file(output_filename)
        except (KeyError, AttributeError, RuntimeError):
            last_fn = created_files[-1] if created_files else "N/A"
            LOG.error("Error while filling in NC file with data: %s", last_fn)
            for fn in created_files:
                if not self.keep_intermediate and os.path.isfile(fn):
                    os.remove(fn)
            raise

        return created_files[-1] if created_files else None