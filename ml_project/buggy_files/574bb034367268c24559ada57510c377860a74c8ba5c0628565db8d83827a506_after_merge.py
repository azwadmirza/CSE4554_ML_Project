def _plot2d(plotfunc):
    """
    Decorator for common 2d plotting logic

    Also adds the 2d plot method to class _PlotMethods
    """
    commondoc = """
    Parameters
    ----------
    darray : DataArray
        Must be 2 dimensional, unless creating faceted plots
    x : string, optional
        Coordinate for x axis. If None use darray.dims[1]
    y : string, optional
        Coordinate for y axis. If None use darray.dims[0]
    figsize : tuple, optional
        A tuple (width, height) of the figure in inches.
        Mutually exclusive with ``size`` and ``ax``.
    aspect : scalar, optional
        Aspect ratio of plot, so that ``aspect * size`` gives the width in
        inches. Only used if a ``size`` is provided.
    size : scalar, optional
        If provided, create a new figure for the plot with the given size.
        Height (in inches) of each plot. See also: ``aspect``.
    ax : matplotlib axes object, optional
        Axis on which to plot this figure. By default, use the current axis.
        Mutually exclusive with ``size`` and ``figsize``.
    row : string, optional
        If passed, make row faceted plots on this dimension name
    col : string, optional
        If passed, make column faceted plots on this dimension name
    col_wrap : integer, optional
        Use together with ``col`` to wrap faceted plots
    xincrease : None, True, or False, optional
        Should the values on the x axes be increasing from left to right?
        if None, use the default for the matplotlib function
    yincrease : None, True, or False, optional
        Should the values on the y axes be increasing from top to bottom?
        if None, use the default for the matplotlib function
    add_colorbar : Boolean, optional
        Adds colorbar to axis
    add_labels : Boolean, optional
        Use xarray metadata to label axes
    vmin, vmax : floats, optional
        Values to anchor the colormap, otherwise they are inferred from the
        data and other keyword arguments. When a diverging dataset is inferred,
        setting one of these values will fix the other by symmetry around
        ``center``. Setting both values prevents use of a diverging colormap.
        If discrete levels are provided as an explicit list, both of these
        values are ignored.
    cmap : matplotlib colormap name or object, optional
        The mapping from data values to color space. If not provided, this
        will be either be ``viridis`` (if the function infers a sequential
        dataset) or ``RdBu_r`` (if the function infers a diverging dataset).
        When `Seaborn` is installed, ``cmap`` may also be a `seaborn`
        color palette. If ``cmap`` is seaborn color palette and the plot type
        is not ``contour`` or ``contourf``, ``levels`` must also be specified.
    colors : discrete colors to plot, optional
        A single color or a list of colors. If the plot type is not ``contour``
        or ``contourf``, the ``levels`` argument is required.
    center : float, optional
        The value at which to center the colormap. Passing this value implies
        use of a diverging colormap. Setting it to ``False`` prevents use of a
        diverging colormap.
    robust : bool, optional
        If True and ``vmin`` or ``vmax`` are absent, the colormap range is
        computed with 2nd and 98th percentiles instead of the extreme values.
    extend : {'neither', 'both', 'min', 'max'}, optional
        How to draw arrows extending the colorbar beyond its limits. If not
        provided, extend is inferred from vmin, vmax and the data limits.
    levels : int or list-like object, optional
        Split the colormap (cmap) into discrete color intervals. If an integer
        is provided, "nice" levels are chosen based on the data range: this can
        imply that the final number of levels is not exactly the expected one.
        Setting ``vmin`` and/or ``vmax`` with ``levels=N`` is equivalent to
        setting ``levels=np.linspace(vmin, vmax, N)``.
    infer_intervals : bool, optional
        Only applies to pcolormesh. If True, the coordinate intervals are
        passed to pcolormesh. If False, the original coordinates are used
        (this can be useful for certain map projections). The default is to
        always infer intervals, unless the mesh is irregular and plotted on
        a map projection.
    subplot_kws : dict, optional
        Dictionary of keyword arguments for matplotlib subplots. Only applies
        to FacetGrid plotting.
    cbar_ax : matplotlib Axes, optional
        Axes in which to draw the colorbar.
    cbar_kwargs : dict, optional
        Dictionary of keyword arguments to pass to the colorbar.
    **kwargs : optional
        Additional arguments to wrapped matplotlib function

    Returns
    -------
    artist :
        The same type of primitive artist that the wrapped matplotlib
        function returns
    """

    # Build on the original docstring
    plotfunc.__doc__ = '%s\n%s' % (plotfunc.__doc__, commondoc)

    @functools.wraps(plotfunc)
    def newplotfunc(darray, x=None, y=None, figsize=None, size=None,
                    aspect=None, ax=None, row=None, col=None,
                    col_wrap=None, xincrease=True, yincrease=True,
                    add_colorbar=None, add_labels=True, vmin=None, vmax=None,
                    cmap=None, center=None, robust=False, extend=None,
                    levels=None, infer_intervals=None, colors=None,
                    subplot_kws=None, cbar_ax=None, cbar_kwargs=None,
                    **kwargs):
        # All 2d plots in xarray share this function signature.
        # Method signature below should be consistent.

        # Decide on a default for the colorbar before facetgrids
        if add_colorbar is None:
            add_colorbar = plotfunc.__name__ != 'contour'

        # Handle facetgrids first
        if row or col:
            allargs = locals().copy()
            allargs.update(allargs.pop('kwargs'))

            # Need the decorated plotting function
            allargs['plotfunc'] = globals()[plotfunc.__name__]

            return _easy_facetgrid(**allargs)

        plt = import_matplotlib_pyplot()

        # colors is mutually exclusive with cmap
        if cmap and colors:
            raise ValueError("Can't specify both cmap and colors.")
        # colors is only valid when levels is supplied or the plot is of type
        # contour or contourf
        if colors and (('contour' not in plotfunc.__name__) and (not levels)):
            raise ValueError("Can only specify colors with contour or levels")
        # we should not be getting a list of colors in cmap anymore
        # is there a better way to do this test?
        if isinstance(cmap, (list, tuple)):
            warnings.warn("Specifying a list of colors in cmap is deprecated. "
                          "Use colors keyword instead.",
                          DeprecationWarning, stacklevel=3)

        xlab, ylab = _infer_xy_labels(darray=darray, x=x, y=y)

        # better to pass the ndarrays directly to plotting functions
        xval = darray[xlab].values
        yval = darray[ylab].values
        zval = darray.to_masked_array(copy=False)

        # May need to transpose for correct x, y labels
        # xlab may be the name of a coord, we have to check for dim names
        if darray[xlab].dims[-1] == darray.dims[0]:
            zval = zval.T

        _ensure_plottable(xval, yval)

        if 'contour' in plotfunc.__name__ and levels is None:
            levels = 7  # this is the matplotlib default

        cmap_kwargs = {'plot_data': zval.data,
                       'vmin': vmin,
                       'vmax': vmax,
                       'cmap': colors if colors else cmap,
                       'center': center,
                       'robust': robust,
                       'extend': extend,
                       'levels': levels,
                       'filled': plotfunc.__name__ != 'contour',
                       }

        cmap_params = _determine_cmap_params(**cmap_kwargs)

        if 'contour' in plotfunc.__name__:
            # extend is a keyword argument only for contour and contourf, but
            # passing it to the colorbar is sufficient for imshow and
            # pcolormesh
            kwargs['extend'] = cmap_params['extend']
            kwargs['levels'] = cmap_params['levels']

        if 'pcolormesh' == plotfunc.__name__:
            kwargs['infer_intervals'] = infer_intervals

        # This allows the user to pass in a custom norm coming via kwargs
        kwargs.setdefault('norm', cmap_params['norm'])

        if 'imshow' == plotfunc.__name__ and isinstance(aspect, basestring):
            # forbid usage of mpl strings
            raise ValueError("plt.imshow's `aspect` kwarg is not available "
                             "in xarray")

        ax = get_axis(figsize, size, aspect, ax)
        primitive = plotfunc(xval, yval, zval, ax=ax, cmap=cmap_params['cmap'],
                             vmin=cmap_params['vmin'],
                             vmax=cmap_params['vmax'],
                             **kwargs)

        # Label the plot with metadata
        if add_labels:
            ax.set_xlabel(xlab)
            ax.set_ylabel(ylab)
            ax.set_title(darray._title_for_slice())

        if add_colorbar:
            cbar_kwargs = {} if cbar_kwargs is None else dict(cbar_kwargs)
            cbar_kwargs.setdefault('extend', cmap_params['extend'])
            if cbar_ax is None:
                cbar_kwargs.setdefault('ax', ax)
            else:
                cbar_kwargs.setdefault('cax', cbar_ax)
            cbar = plt.colorbar(primitive, **cbar_kwargs)
            if darray.name and add_labels and 'label' not in cbar_kwargs:
                cbar.set_label(darray.name, rotation=90)
        elif cbar_ax is not None or cbar_kwargs is not None:
            # inform the user about keywords which aren't used
            raise ValueError("cbar_ax and cbar_kwargs can't be used with "
                             "add_colorbar=False.")

        _update_axes_limits(ax, xincrease, yincrease)

        return primitive

    # For use as DataArray.plot.plotmethod
    @functools.wraps(newplotfunc)
    def plotmethod(_PlotMethods_obj, x=None, y=None, figsize=None, size=None,
                   aspect=None, ax=None, row=None, col=None, col_wrap=None,
                   xincrease=True, yincrease=True, add_colorbar=None,
                   add_labels=True, vmin=None, vmax=None, cmap=None,
                   colors=None, center=None, robust=False, extend=None,
                   levels=None, infer_intervals=None, subplot_kws=None,
                   cbar_ax=None, cbar_kwargs=None, **kwargs):
        """
        The method should have the same signature as the function.

        This just makes the method work on Plotmethods objects,
        and passes all the other arguments straight through.
        """
        allargs = locals()
        allargs['darray'] = _PlotMethods_obj._da
        allargs.update(kwargs)
        for arg in ['_PlotMethods_obj', 'newplotfunc', 'kwargs']:
            del allargs[arg]
        return newplotfunc(**allargs)

    # Add to class _PlotMethods
    setattr(_PlotMethods, plotmethod.__name__, plotmethod)

    return newplotfunc