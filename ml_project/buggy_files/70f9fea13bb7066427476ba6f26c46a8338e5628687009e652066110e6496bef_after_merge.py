    def _add_proj4_string(self, datasets, first_dataset):
        proj4_string = " Proj string: "

        if isinstance(datasets, list):
            proj4_string += first_dataset.attrs['area'].proj4_string
        else:
            proj4_string += datasets.attrs['area'].proj4_string

        x_0 = 0
        y_0 = 0
        if 'EPSG:32631' in proj4_string:
            proj4_string = proj4_string.replace("+init=EPSG:32631",
                                                "+proj=etmerc +lat_0=0 +lon_0=3 +k=0.9996 +ellps=WGS84 +datum=WGS84")
            x_0 = 500000
        elif 'EPSG:32632' in proj4_string:
            proj4_string = proj4_string.replace("+init=EPSG:32632",
                                                "+proj=etmerc +lat_0=0 +lon_0=9 +k=0.9996 +ellps=WGS84 +datum=WGS84")
            x_0 = 500000
        elif 'EPSG:32633' in proj4_string:
            proj4_string = proj4_string.replace("+init=EPSG:32633",
                                                "+proj=etmerc +lat_0=0 +lon_0=15 +k=0.9996 +ellps=WGS84 +datum=WGS84")
            x_0 = 500000
        elif 'EPSG:32634' in proj4_string:
            proj4_string = proj4_string.replace("+init=EPSG:32634",
                                                "+proj=etmerc +lat_0=0 +lon_0=21 +k=0.9996 +ellps=WGS84 +datum=WGS84")
            x_0 = 500000
        elif 'EPSG:32635' in proj4_string:
            proj4_string = proj4_string.replace("+init=EPSG:32635",
                                                "+proj=etmerc +lat_0=0 +lon_0=27 +k=0.9996 +ellps=WGS84 +datum=WGS84")
            x_0 = 500000
        elif 'EPSG' in proj4_string:
            LOG.warning("EPSG used in proj string but not converted. Please add this in code")

        if 'geos' in proj4_string:
            proj4_string = proj4_string.replace("+sweep=x ", "")
            if '+a=6378137.0 +b=6356752.31414' in proj4_string:
                proj4_string = proj4_string.replace("+a=6378137.0 +b=6356752.31414",
                                                    "+ellps=WGS84")
            if '+units=m' in proj4_string:
                proj4_string = proj4_string.replace("+units=m", "+units=km")

        if not any(datum in proj4_string for datum in ['datum', 'towgs84']):
            proj4_string += ' +towgs84=0,0,0'

        if 'units' not in proj4_string:
            proj4_string += ' +units=km'

        if isinstance(datasets, list):
            proj4_string += ' +x_0=%.6f' % (
                (-first_dataset.attrs['area'].area_extent[0] +
                 first_dataset.attrs['area'].pixel_size_x) + x_0)
            proj4_string += ' +y_0=%.6f' % (
                (-first_dataset.attrs['area'].area_extent[1] +
                 first_dataset.attrs['area'].pixel_size_y) + y_0)
        else:
            proj4_string += ' +x_0=%.6f' % (
                (-datasets.attrs['area'].area_extent[0] +
                 datasets.attrs['area'].pixel_size_x) + x_0)
            proj4_string += ' +y_0=%.6f' % (
                (-datasets.attrs['area'].area_extent[1] +
                 datasets.attrs['area'].pixel_size_y) + y_0)

        LOG.debug("proj4_string: %s", proj4_string)
        proj4_string += '\n'

        return proj4_string