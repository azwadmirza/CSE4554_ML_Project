def _imshow_tfr(ax, ch_idx, tmin, tmax, vmin, vmax, onselect, ylim=None,
                tfr=None, freq=None, vline=None, x_label=None, y_label=None,
                colorbar=False, picker=True, cmap='RdBu_r', title=None,
                hline=None):
    """ Aux function to show time-freq map on topo """
    import matplotlib.pyplot as plt
    from matplotlib.widgets import RectangleSelector

    extent = (tmin, tmax, freq[0], freq[-1])
    img = ax.imshow(tfr[ch_idx], extent=extent, aspect="auto", origin="lower",
                    vmin=vmin, vmax=vmax, picker=picker, cmap=cmap)
    if isinstance(ax, plt.Axes):
        if x_label is not None:
            ax.set_xlabel(x_label)
        if y_label is not None:
            ax.set_ylabel(y_label)
    else:
        if x_label is not None:
            plt.xlabel(x_label)
        if y_label is not None:
            plt.ylabel(y_label)
    if colorbar:
        plt.colorbar(mappable=img)
    if title:
        plt.title(title)
    if not isinstance(ax, plt.Axes):
        ax = plt.gca()
    ax.RS = RectangleSelector(ax, onselect=onselect)  # reference must be kept