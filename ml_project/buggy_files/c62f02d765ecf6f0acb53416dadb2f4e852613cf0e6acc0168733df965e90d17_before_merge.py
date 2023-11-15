    def barbs(self, x, y, u, v, *args, **kwargs):
        """
        Plot a 2-D field of barbs.

        Extra Kwargs:

        * transform: :class:`cartopy.crs.Projection` or matplotlib transform
            The coordinate system in which the vectors are defined.

        * regrid_shape: int or 2-tuple of ints
            If given, specifies that the points where the arrows are
            located will be interpolated onto a regular grid in
            projection space. If a single integer is given then that
            will be used as the minimum grid length dimension, while the
            other dimension will be scaled up according to the target
            extent's aspect ratio. If a pair of ints are given they
            determine the grid length in the x and y directions
            respectively.

        * target_extent: 4-tuple
            If given, specifies the extent in the target CRS that the
            regular grid defined by *regrid_shape* will have. Defaults
            to the current extent of the map projection.

        See :func:`matplotlib.pyplot.barbs` for details on arguments
        and keyword arguments.

        .. note::

           The vector components must be defined as grid eastward and
           grid northward.

        """
        t = kwargs.get('transform', None)
        if t is None:
            t = self.projection
        if isinstance(t, ccrs.CRS) and not isinstance(t, ccrs.Projection):
            raise ValueError('invalid transform:'
                             ' Spherical barbs are not supported - '
                             ' consider using PlateCarree/RotatedPole.')
        if isinstance(t, ccrs.Projection):
            kwargs['transform'] = t._as_mpl_transform(self)
        else:
            kwargs['transform'] = t
        regrid_shape = kwargs.pop('regrid_shape', None)
        target_extent = kwargs.pop('target_extent',
                                   self.get_extent(self.projection))
        if regrid_shape is not None:
            # If regridding is required then we'll be handling transforms
            # manually and plotting in native coordinates.
            regrid_shape = self._regrid_shape_aspect(regrid_shape,
                                                     target_extent)
            if args:
                # Interpolate color array as well as vector components.
                x, y, u, v, c = vector_scalar_to_grid(
                    t, self.projection, regrid_shape, x, y, u, v, args[0],
                    target_extent=target_extent)
                args = (c,) + args[1:]
            else:
                x, y, u, v = vector_scalar_to_grid(
                    t, self.projection, regrid_shape, x, y, u, v,
                    target_extent=target_extent)
            kwargs.pop('transform', None)
        elif t != self.projection:
            # Transform the vectors if the projection is not the same as the
            # data transform.
            if x.ndim == 1 and y.ndim == 1:
                x, y = np.meshgrid(x, y)
            u, v = self.projection.transform_vectors(t, x, y, u, v)
        return matplotlib.axes.Axes.barbs(self, x, y, u, v, *args, **kwargs)