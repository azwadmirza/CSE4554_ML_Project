    def _make_area_from_coords(self, coords):
        """Create an apropriate area with the given *coords*."""
        if len(coords) == 2:
            lon_sn = coords[0].info.get('standard_name')
            lat_sn = coords[1].info.get('standard_name')
            if lon_sn == 'longitude' and lat_sn == 'latitude':
                sdef = SwathDefinition(*coords)
                sensor_str = sdef.name = '_'.join(self.info['sensors'])
                shape_str = '_'.join(map(str, coords[0].shape))
                sdef.name = "{}_{}_{}_{}".format(sensor_str, shape_str,
                                                 coords[0].info['name'],
                                                 coords[1].info['name'])
                return sdef
            else:
                raise ValueError(
                    'Coordinates info object missing standard_name key: ' +
                    str(coords))
        elif len(coords) != 0:
            raise NameError("Don't know what to do with coordinates " + str(
                coords))