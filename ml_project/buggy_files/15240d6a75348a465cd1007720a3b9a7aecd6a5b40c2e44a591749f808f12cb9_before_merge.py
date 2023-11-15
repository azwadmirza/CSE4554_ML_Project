def _plot_topomap_multi_cbar(data, pos, ax, title=None, unit=None,
                             vmin=None, vmax=None, cmap='RdBu_r',
                             colorbar=False, cbar_fmt='%3.3f'):
    """Aux Function"""
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    _hide_frame(ax)
    vmin = np.min(data) if vmin is None else vmin
    vmax = np.max(data) if vmax is None else vmax

    if title is not None:
        ax.set_title(title, fontsize=10)
    im, _ = plot_topomap(data, pos, vmin=vmin, vmax=vmax, axes=ax,
                         cmap=cmap, image_interp='bilinear', contours=False,
                         show=False)

    if colorbar is True:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="10%", pad=0.25)
        cbar = plt.colorbar(im, cax=cax, format=cbar_fmt)
        cbar.set_ticks((vmin, vmax))
        if unit is not None:
            cbar.ax.set_title(unit, fontsize=8)
        cbar.ax.tick_params(labelsize=8)