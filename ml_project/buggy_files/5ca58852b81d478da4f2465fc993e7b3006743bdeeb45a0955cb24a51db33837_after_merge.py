def _fig_to_img(fig, image_format='png', scale=None, **kwargs):
    """Plot figure and create a binary image."""
    # fig can be ndarray, mpl Figure, Mayavi Figure, or callable that produces
    # a mpl Figure
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    if isinstance(fig, np.ndarray):
        fig = _ndarray_to_fig(fig)
    elif callable(fig):
        plt.close('all')
        fig = fig(**kwargs)
    elif not isinstance(fig, Figure):
        mlab = None
        try:
            mlab = _import_mlab()
        # on some systems importing Mayavi raises SystemExit (!)
        except Exception:
            is_mayavi = False
        else:
            import mayavi
            is_mayavi = isinstance(fig, mayavi.core.scene.Scene)
        if not is_mayavi:
            raise TypeError('Each fig must be a matplotlib Figure, mayavi '
                            'Scene, or NumPy ndarray, got %s (type %s)'
                            % (fig, type(fig)))
        if fig.scene is not None:
            img = mlab.screenshot(figure=fig)
        else:  # Testing mode
            img = np.zeros((2, 2, 3))

        mlab.close(fig)
        fig = _ndarray_to_fig(img)

    output = BytesIO()
    if scale is not None:
        _scale_mpl_figure(fig, scale)
    logger.debug('Saving figure %s with dpi %s'
                 % (fig.get_size_inches(), fig.get_dpi()))
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('ignore')  # incompatible axes
        fig.savefig(output, format=image_format, dpi=fig.get_dpi(),
                    bbox_to_inches='tight')
    plt.close(fig)
    output = output.getvalue()
    return (output.decode('utf-8') if image_format == 'svg' else
            base64.b64encode(output).decode('ascii'))