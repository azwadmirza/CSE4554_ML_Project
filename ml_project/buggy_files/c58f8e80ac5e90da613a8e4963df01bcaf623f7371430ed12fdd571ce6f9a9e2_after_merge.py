    def from_crs(crs_from, crs_to, skip_equivalent=False, always_xy=False):
        """Make a Transformer from a :obj:`~pyproj.crs.CRS` or input used to create one.

        Parameters
        ----------
        crs_from: ~pyproj.crs.CRS or input used to create one
            Projection of input data.
        crs_to: ~pyproj.crs.CRS or input used to create one
            Projection of output data.
        skip_equivalent: bool, optional
            If true, will skip the transformation operation if input and output
            projections are equivalent. Default is false.
        always_xy: bool, optional
            If true, the transform method will accept as input and return as output
            coordinates using the traditional GIS order, that is longitude, latitude
            for geographic CRS and easting, northing for most projected CRS.
            Default is false.

        Returns
        -------
        :obj:`~Transformer`

        """
        transformer = Transformer(
            _Transformer.from_crs(
                CRS.from_user_input(crs_from),
                CRS.from_user_input(crs_to),
                skip_equivalent=skip_equivalent,
                always_xy=always_xy,
            )
        )
        return transformer