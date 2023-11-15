def lb_forecast(sh_order):
    r"""Returns the Laplace-Beltrami regularization matrix for FORECAST
    """
    n_c = int((sh_order + 1)*(sh_order + 2)/2)
    diag_lb = np.zeros(n_c)
    counter = 0
    for l in range(0, sh_order + 1, 2):
        for m in range(-l, l + 1):
            diag_lb[counter] = (l * (l + 1)) ** 2
            counter += 1

    return np.diag(diag_lb)