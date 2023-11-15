    def from_proj(proj_from, proj_to, skip_equivalent=False, always_xy=False):
        """Make a Transformer from a :obj:`~pyproj.proj.Proj` or input used to create one.

        Parameters
        ----------
        proj_from: :obj:`~pyproj.proj.Proj` or input used to create one
            Projection of input data.
        proj_to: :obj:`~pyproj.proj.Proj` or input used to create one
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
        if not isinstance(proj_from, Proj):
            proj_from = Proj(proj_from)
        if not isinstance(proj_to, Proj):
            proj_to = Proj(proj_to)

        return Transformer(
            _Transformer.from_crs(
                proj_from.crs,
                proj_to.crs,
                skip_equivalent=skip_equivalent,
                always_xy=always_xy,
            )
        )