def lb_forecast(sh_order):
    r"""Returns the Laplace-Beltrami regularization matrix for FORECAST
    """
    n_c = int((sh_order + 1)*(sh_order + 2)/2)
    diag_lb = np.zeros(n_c)
    counter = 0
    for l in range(0, sh_order + 1, 2):
        stop = 2 * l + 1 + counter
        diag_lb[counter:stop] = (l * (l + 1)) ** 2
        counter = stop

    return np.diag(diag_lb)