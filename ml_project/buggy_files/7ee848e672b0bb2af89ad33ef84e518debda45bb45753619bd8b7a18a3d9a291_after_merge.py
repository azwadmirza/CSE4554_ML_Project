    def _make_area_from_coords(self, coords):
        """Create an appropriate area with the given *coords*."""
        if len(coords) == 2:
            lon_sn = coords[0].attrs.get('standard_name')
            lat_sn = coords[1].attrs.get('standard_name')
            if lon_sn == 'longitude' and lat_sn == 'latitude':
                key = None
                try:
                    key = (coords[0].data.name, coords[1].data.name)
                    sdef = self.coords_cache.get(key)
                except AttributeError:
                    sdef = None
                if sdef is None:
                    sdef = SwathDefinition(*coords)
                    if key is not None:
                        self.coords_cache[key] = sdef
                sensor_str = '_'.join(self.info['sensors'])
                shape_str = '_'.join(map(str, coords[0].shape))
                sdef.name = "{}_{}_{}_{}".format(sensor_str, shape_str,
                                                 coords[0].attrs['name'],
                                                 coords[1].attrs['name'])
                return sdef
            else:
                raise ValueError(
                    'Coordinates info object missing standard_name key: ' +
                    str(coords))
        elif len(coords) != 0:
            raise NameError("Don't know what to do with coordinates " + str(
                coords))