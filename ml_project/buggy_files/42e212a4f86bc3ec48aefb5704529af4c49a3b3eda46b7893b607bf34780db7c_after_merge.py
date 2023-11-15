def plot_projs_topomap(projs, layout=None, cmap=None, sensors=True,
                       colorbar=False, res=64, size=1, show=True,
                       outlines='head', contours=6, image_interp='bilinear',
                       axes=None):
    """Plot topographic maps of SSP projections

    Parameters
    ----------
    projs : list of Projection
        The projections
    layout : None | Layout | list of Layout
        Layout instance specifying sensor positions (does not need to be
        specified for Neuromag data). Or a list of Layout if projections
        are from different sensor types.
    cmap : matplotlib colormap | (colormap, bool) | 'interactive' | None
        Colormap to use. If tuple, the first value indicates the colormap to
        use and the second value is a boolean defining interactivity. In
        interactive mode (only works if ``colorbar=True``) the colors are
        adjustable by clicking and dragging the colorbar with left and right
        mouse button. Left mouse button moves the scale up and down and right
        mouse button adjusts the range. Hitting space bar resets the range. Up
        and down arrows can be used to change the colormap. If None (default),
        'Reds' is used for all positive data, otherwise defaults to 'RdBu_r'.
        If 'interactive', translates to (None, True).
    sensors : bool | str
        Add markers for sensor locations to the plot. Accepts matplotlib plot
        format string (e.g., 'r+' for red plusses). If True, a circle will be
        used (via .add_artist). Defaults to True.
    colorbar : bool
        Plot a colorbar.
    res : int
        The resolution of the topomap image (n pixels along each side).
    size : scalar
        Side length of the topomaps in inches (only applies when plotting
        multiple topomaps at a time).
    show : bool
        Show figure if True.
    outlines : 'head' | 'skirt' | dict | None
        The outlines to be drawn. If 'head', the default head scheme will be
        drawn. If 'skirt' the head scheme will be drawn, but sensors are
        allowed to be plotted outside of the head circle. If dict, each key
        refers to a tuple of x and y positions, the values in 'mask_pos' will
        serve as image mask, and the 'autoshrink' (bool) field will trigger
        automated shrinking of the positions due to points outside the outline.
        Alternatively, a matplotlib patch object can be passed for advanced
        masking options, either directly or as a function that returns patches
        (required for multi-axis plots). If None, nothing will be drawn.
        Defaults to 'head'.
    contours : int | False | None
        The number of contour lines to draw. If 0, no contours will be drawn.
    image_interp : str
        The image interpolation to be used. All matplotlib options are
        accepted.
    axes : instance of Axes | list | None
        The axes to plot to. If list, the list must be a list of Axes of
        the same length as the number of projectors. If instance of Axes,
        there must be only one projector. Defaults to None.

    Returns
    -------
    fig : instance of matplotlib figure
        Figure distributing one image per channel across sensor topography.

    Notes
    -----
    .. versionadded:: 0.9.0
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    if layout is None:
        from ..channels import read_layout
        layout = read_layout('Vectorview-all')

    if not isinstance(layout, list):
        layout = [layout]

    n_projs = len(projs)
    nrows = math.floor(math.sqrt(n_projs))
    ncols = math.ceil(n_projs / nrows)

    if cmap == 'interactive':
        cmap = (None, True)
    elif not isinstance(cmap, tuple):
        cmap = (cmap, True)
    if axes is None:
        plt.figure()
        axes = list()
        for idx in range(len(projs)):
            ax = plt.subplot(nrows, ncols, idx + 1)
            axes.append(ax)
    elif isinstance(axes, plt.Axes):
        axes = [axes]
    if len(axes) != len(projs):
        raise RuntimeError('There must be an axes for each picked projector.')
    for proj_idx, proj in enumerate(projs):
        axes[proj_idx].set_title(proj['desc'][:10] + '...')
        ch_names = _clean_names(proj['data']['col_names'])
        data = proj['data']['data'].ravel()

        idx = []
        for l in layout:
            is_vv = l.kind.startswith('Vectorview')
            if is_vv:
                from ..channels.layout import _pair_grad_sensors_from_ch_names
                grad_pairs = _pair_grad_sensors_from_ch_names(ch_names)
                if grad_pairs:
                    ch_names = [ch_names[i] for i in grad_pairs]

            idx = [l.names.index(c) for c in ch_names if c in l.names]
            if len(idx) == 0:
                continue

            pos = l.pos[idx]
            if is_vv and grad_pairs:
                from ..channels.layout import _merge_grad_data
                shape = (len(idx) // 2, 2, -1)
                pos = pos.reshape(shape).mean(axis=1)
                data = _merge_grad_data(data[grad_pairs]).ravel()

            break

        if len(idx):
            im = plot_topomap(data, pos[:, :2], vmax=None, cmap=cmap[0],
                              sensors=sensors, res=res, axes=axes[proj_idx],
                              outlines=outlines, contours=contours,
                              image_interp=image_interp, show=False)[0]
            if colorbar:
                divider = make_axes_locatable(axes[proj_idx])
                cax = divider.append_axes("right", size="5%", pad=0.05)
                cbar = plt.colorbar(im, cax=cax, cmap=cmap)
                if cmap[1]:
                    axes[proj_idx].CB = DraggableColorbar(cbar, im)
        else:
            raise RuntimeError('Cannot find a proper layout for projection %s'
                               % proj['desc'])
    tight_layout(fig=axes[0].get_figure())
    plt_show(show)
    return axes[0].get_figure()