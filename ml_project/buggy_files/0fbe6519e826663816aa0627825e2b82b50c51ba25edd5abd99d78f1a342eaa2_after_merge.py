    def world_to_pixel(self, coordinate, origin=None):
        """
        Convert a world (data) coordinate to a pixel coordinate.

        Parameters
        ----------
        coordinate : `~astropy.coordinates.SkyCoord` or `~astropy.coordinates.BaseFrame`
            The coordinate object to convert to pixel coordinates.

        origin : int
            Deprecated.

            Origin of the top-left corner. i.e. count from 0 or 1.
            Normally, origin should be 0 when passing numpy indices, or 1 if
            passing values from FITS header or map attributes.

        Returns
        -------
        x : `~astropy.units.Quantity`
            Pixel coordinate on the CTYPE1 axis.

        y : `~astropy.units.Quantity`
            Pixel coordinate on the CTYPE2 axis.
        """
        self._check_origin(origin)
        x, y = self.wcs.world_to_pixel(coordinate)
        if origin == 1:
            x += 1
            y += 1

        return PixelPair(x * u.pixel, y * u.pixel)