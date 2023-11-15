def pzmap(sys, plot=True, grid=False, title='Pole Zero Map', **kwargs):
    """
    Plot a pole/zero map for a linear system.

    Parameters
    ----------
    sys: LTI (StateSpace or TransferFunction)
        Linear system for which poles and zeros are computed.
    plot: bool, optional
        If ``True`` a graph is generated with Matplotlib,
        otherwise the poles and zeros are only computed and returned.
    grid: boolean (default = False)
        If True plot omega-damping grid.

    Returns
    -------
    pole: array
        The systems poles
    zeros: array
        The system's zeros.
    """
    # Check to see if legacy 'Plot' keyword was used
    if 'Plot' in kwargs:
        import warnings
        warnings.warn("'Plot' keyword is deprecated in pzmap; use 'plot'",
                      FutureWarning)
        plot = kwargs['Plot']

    # Get parameter values
    plot = config._get_param('rlocus', 'plot', plot, True)
    grid = config._get_param('rlocus', 'grid', grid, False)

    if not isinstance(sys, LTI):
        raise TypeError('Argument ``sys``: must be a linear system.')

    poles = sys.pole()
    zeros = sys.zero()

    if (plot):
        import matplotlib.pyplot as plt

        if grid:
            if isdtime(sys, strict=True):
                ax, fig = zgrid()
            else:
                ax, fig = sgrid()
        else:
            ax, fig = nogrid()

        # Plot the locations of the poles and zeros
        if len(poles) > 0:
            ax.scatter(real(poles), imag(poles), s=50, marker='x',
                       facecolors='k')
        if len(zeros) > 0:
            ax.scatter(real(zeros), imag(zeros), s=50, marker='o',
                       facecolors='none', edgecolors='k')

        plt.title(title)

    # Return locations of poles and zeros as a tuple
    return poles, zeros