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

        import matplotlib.pyplot as plt

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