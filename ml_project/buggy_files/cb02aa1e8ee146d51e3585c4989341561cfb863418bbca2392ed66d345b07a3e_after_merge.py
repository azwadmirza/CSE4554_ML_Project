    def pixel_to_world(self, x: u.pixel, y: u.pixel, origin=None):
        """
        Convert a pixel coordinate to a data (world) coordinate.

        Parameters
        ----------
        x : `~astropy.units.Quantity`
            Pixel coordinate of the CTYPE1 axis. (Normally solar-x).

        y : `~astropy.units.Quantity`
            Pixel coordinate of the CTYPE2 axis. (Normally solar-y).

        origin : int
            Deprecated.

            Origin of the top-left corner. i.e. count from 0 or 1.
            Normally, origin should be 0 when passing numpy indices, or 1 if
            passing values from FITS header or map attributes.

        Returns
        -------
        coord : `astropy.coordinates.SkyCoord`
            A coordinate object representing the output coordinate.
        """
        self._check_origin(origin)
        if origin == 1:
            x = x - 1 * u.pixel
            y = y - 1 * u.pixel

        return self.wcs.pixel_to_world(x, y)