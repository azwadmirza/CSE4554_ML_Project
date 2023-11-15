    def scatter(self, x, y, s=20, c=None, marker='o', cmap=None, norm=None,
                vmin=None, vmax=None, alpha=None, linewidths=None,
                verts=None, edgecolors=None,
                **kwargs):
        """
        Make a scatter plot of x vs y, where x and y are sequence like objects
        of the same length.

        Parameters
        ----------
        x, y : array_like, shape (n, )
            Input data

        s : scalar or array_like, shape (n, ), optional, default: 20
            size in points^2.

        c : color, sequence, or sequence of color, optional, default: 'b'
            `c` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs
            (see below). Note that `c` should not be a single numeric RGB or
            RGBA sequence because that is indistinguishable from an array of
            values to be colormapped.  `c` can be a 2-D array in which the
            rows are RGB or RGBA, however, including the case of a single
            row to specify the same color for all points.

        marker : `~matplotlib.markers.MarkerStyle`, optional, default: 'o'
            See `~matplotlib.markers` for more information on the different
            styles of markers scatter supports. `marker` can be either
            an instance of the class or the text shorthand for a particular
            marker.

        cmap : `~matplotlib.colors.Colormap`, optional, default: None
            A `~matplotlib.colors.Colormap` instance or registered name.
            `cmap` is only used if `c` is an array of floats. If None,
            defaults to rc `image.cmap`.

        norm : `~matplotlib.colors.Normalize`, optional, default: None
            A `~matplotlib.colors.Normalize` instance is used to scale
            luminance data to 0, 1. `norm` is only used if `c` is an array of
            floats. If `None`, use the default :func:`normalize`.

        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.  Note if you pass a `norm` instance, your
            settings for `vmin` and `vmax` will be ignored.

        alpha : scalar, optional, default: None
            The alpha blending value, between 0 (transparent) and 1 (opaque)

        linewidths : scalar or array_like, optional, default: None
            If None, defaults to (lines.linewidth,).

        edgecolors : color or sequence of color, optional, default: None
            If None, defaults to (patch.edgecolor).
            If 'face', the edge color will always be the same as
            the face color.  If it is 'none', the patch boundary will not
            be drawn.  For non-filled markers, the `edgecolors` kwarg
            is ignored; color is determined by `c`.

        Returns
        -------
        paths : `~matplotlib.collections.PathCollection`

        Other parameters
        ----------------
        kwargs : `~matplotlib.collections.Collection` properties

        Notes
        ------
        Any or all of `x`, `y`, `s`, and `c` may be masked arrays, in
        which case all masks will be combined and only unmasked points
        will be plotted.

        Fundamentally, scatter works with 1-D arrays; `x`, `y`, `s`,
        and `c` may be input as 2-D arrays, but within scatter
        they will be flattened. The exception is `c`, which
        will be flattened only if its size matches the size of `x`
        and `y`.

        Examples
        --------
        .. plot:: mpl_examples/shapes_and_collections/scatter_demo.py

        """

        if not self._hold:
            self.cla()

        # Process **kwargs to handle aliases, conflicts with explicit kwargs:

        facecolors = None
        ec = kwargs.pop('edgecolor', None)
        if ec is not None:
            edgecolors = ec
        fc = kwargs.pop('facecolor', None)
        if fc is not None:
            facecolors = fc
        fc = kwargs.pop('facecolors', None)
        if fc is not None:
            facecolors = fc
        # 'color' should be deprecated in scatter, or clearly defined;
        # since it isn't, I am giving it low priority.
        co = kwargs.pop('color', None)
        if co is not None:
            if edgecolors is None:
                edgecolors = co
            if facecolors is None:
                facecolors = co
        if c is None:
            if facecolors is not None:
                c = facecolors
            else:
                c = 'b'  # The original default

        self._process_unit_info(xdata=x, ydata=y, kwargs=kwargs)
        x = self.convert_xunits(x)
        y = self.convert_yunits(y)

        # np.ma.ravel yields an ndarray, not a masked array,
        # unless its argument is a masked array.
        x = np.ma.ravel(x)
        y = np.ma.ravel(y)
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        s = np.ma.ravel(s)  # This doesn't have to match x, y in size.

        # After this block, c_array will be None unless
        # c is an array for mapping.  The potential ambiguity
        # with a sequence of 3 or 4 numbers is resolved in
        # favor of mapping, not rgb or rgba.
        try:
            c_array = np.asanyarray(c, dtype=float)
            if c_array.size == x.size:
                c = np.ma.ravel(c_array)
            else:
                # Wrong size; it must not be intended for mapping.
                c_array = None
        except ValueError:
            # Failed to make a floating-point array; c must be color specs.
            c_array = None

        if c_array is None:
            colors = c     # must be acceptable as PathCollection facecolors
        else:
            colors = None  # use cmap, norm after collection is created

        # c will be unchanged unless it is the same length as x:
        x, y, s, c = cbook.delete_masked_points(x, y, s, c)

        scales = s   # Renamed for readability below.

        # to be API compatible
        if marker is None and not (verts is None):
            marker = (verts, 0)
            verts = None

        if isinstance(marker, mmarkers.MarkerStyle):
            marker_obj = marker
        else:
            marker_obj = mmarkers.MarkerStyle(marker)

        path = marker_obj.get_path().transformed(
            marker_obj.get_transform())
        if not marker_obj.is_filled():
            edgecolors = 'face'

        offsets = np.dstack((x, y))

        collection = mcoll.PathCollection(
                (path,), scales,
                facecolors=colors,
                edgecolors=edgecolors,
                linewidths=linewidths,
                offsets=offsets,
                transOffset=kwargs.pop('transform', self.transData),
                alpha=alpha
                )
        collection.set_transform(mtransforms.IdentityTransform())
        collection.update(kwargs)

        if colors is None:
            if norm is not None and not isinstance(norm, mcolors.Normalize):
                msg = "'norm' must be an instance of 'mcolors.Normalize'"
                raise ValueError(msg)
            collection.set_array(np.asarray(c))
            collection.set_cmap(cmap)
            collection.set_norm(norm)

            if vmin is not None or vmax is not None:
                collection.set_clim(vmin, vmax)
            else:
                collection.autoscale_None()

        # The margin adjustment is a hack to deal with the fact that we don't
        # want to transform all the symbols whose scales are in points
        # to data coords to get the exact bounding box for efficiency
        # reasons.  It can be done right if this is deemed important.
        # Also, only bother with this padding if there is anything to draw.
        if self._xmargin < 0.05 and x.size > 0:
            self.set_xmargin(0.05)

        if self._ymargin < 0.05 and x.size > 0:
            self.set_ymargin(0.05)

        self.add_collection(collection)
        self.autoscale_view()

        return collection