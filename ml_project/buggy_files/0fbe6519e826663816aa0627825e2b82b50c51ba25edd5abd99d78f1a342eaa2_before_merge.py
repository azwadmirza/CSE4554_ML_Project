    def world_to_pixel(self, coordinate, origin=0):
        """
        Convert a world (data) coordinate to a pixel coordinate by using
        `~astropy.wcs.WCS.wcs_world2pix`.

        Parameters
        ----------
        coordinate : `~astropy.coordinates.SkyCoord` or `~astropy.coordinates.BaseFrame`
            The coordinate object to convert to pixel coordinates.

        origin : int
            Origin of the top-left corner. i.e. count from 0 or 1.
            Normally, origin should be 0 when passing numpy indices, or 1 if
            passing values from FITS header or map attributes.
            See `~astropy.wcs.WCS.wcs_world2pix` for more information.

        Returns
        -------
        x : `~astropy.units.Quantity`
            Pixel coordinate on the CTYPE1 axis.

        y : `~astropy.units.Quantity`
            Pixel coordinate on the CTYPE2 axis.
        """
        if not isinstance(coordinate, (SkyCoord,
                                       astropy.coordinates.BaseCoordinateFrame)):
            raise ValueError(
                "world_to_pixel takes a Astropy coordinate frame or SkyCoord instance.")

        native_frame = coordinate.transform_to(self.coordinate_frame)
        lon, lat = u.Quantity(self._get_lon_lat(native_frame)).to(u.deg)
        x, y = self.wcs.wcs_world2pix(lon, lat, origin)

        return PixelPair(x * u.pixel, y * u.pixel)