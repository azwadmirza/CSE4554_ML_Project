    def _validate_meta(self, meta):
        """
        Validate a meta argument for use as metadata.
        Currently only validates by class.
        """
        if isinstance(meta, astropy.io.fits.header.Header):
            return True
        elif isinstance(meta, sunpy.io.header.FileHeader):
            return True
        elif isinstance(meta, dict):
            return True
        else:
            return False