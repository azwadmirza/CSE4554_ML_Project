    def pixel_to_world(self, x: u.pixel, y: u.pixel, origin=0):
        """
        Convert a pixel coordinate to a data (world) coordinate by using
        `~astropy.wcs.WCS.wcs_pix2world`.

        Parameters
        ----------

        x : `~astropy.units.Quantity`
            Pixel coordinate of the CTYPE1 axis. (Normally solar-x).

        y : `~astropy.units.Quantity`
            Pixel coordinate of the CTYPE2 axis. (Normally solar-y).

        origin : int
            Origin of the top-left corner. i.e. count from 0 or 1.
            Normally, origin should be 0 when passing numpy indices, or 1 if
            passing values from FITS header or map attributes.
            See `~astropy.wcs.WCS.wcs_pix2world` for more information.

        Returns
        -------

        coord : `astropy.coordinates.SkyCoord`
            A coordinate object representing the output coordinate.

        """

        # Hold the WCS instance here so we can inspect the output units after
        # the pix2world call
        temp_wcs = self.wcs

        x, y = temp_wcs.wcs_pix2world(x, y, origin)

        out_units = list(map(u.Unit, temp_wcs.wcs.cunit))

        x = u.Quantity(x, out_units[0])
        y = u.Quantity(y, out_units[1])

        return SkyCoord(x, y, frame=self.coordinate_frame)