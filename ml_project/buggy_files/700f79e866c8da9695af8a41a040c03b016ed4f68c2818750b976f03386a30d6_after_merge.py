def mask_source_lonlats(source_def, mask):
    """Mask source longitudes and latitudes to match data mask"""
    source_geo_def = source_def

    # the data may have additional masked pixels
    # let's compare them to see if we can use the same area
    # assume lons and lats mask are the same
    if isinstance(source_geo_def, SwathDefinition):
        if np.issubsctype(mask.dtype, np.bool):
            # copy the source area and use it for the rest of the calculations
            LOG.debug("Copying source area to mask invalid dataset points")
            # source_geo_def = deepcopy(source_geo_def)
            # lons, lats = source_geo_def.get_lonlats()
            if np.ndim(mask) == 3:
                # FIXME: we should treat 3d arrays (composites) layer by layer!
                mask = np.sum(mask, axis=2)
                # FIXME: pyresample doesn't seem to like this
                # lons = np.tile(lons, (1, 1, mask.shape[2]))
                # lats = np.tile(lats, (1, 1, mask.shape[2]))

            # use the same data, but make a new mask (i.e. don't affect the original masked array)
            # the ma.array function combines the undelying mask with the new
            # one (OR)
            source_geo_def.lons = source_geo_def.lons.where(~mask)
            source_geo_def.lats = source_geo_def.lats.where(~mask)
            # source_geo_def.lons = np.ma.array(lons, mask=mask)
            # source_geo_def.lats = np.ma.array(lats, mask=mask)
        else:
            import xarray.ufuncs as xu
            return SwathDefinition(source_geo_def.lons.where(~xu.isnan(mask)),
                                   source_geo_def.lats.where(~xu.isnan(mask)))
            # This was evil
            # source_geo_def.lons = source_geo_def.lons.where(~xu.isnan(mask))
            # source_geo_def.lats = source_geo_def.lats.where(~xu.isnan(mask))

    return source_geo_def