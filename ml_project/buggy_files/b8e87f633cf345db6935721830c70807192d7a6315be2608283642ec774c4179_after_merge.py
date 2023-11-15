def _make_arma_exog(endog, exog, trend):
    k_trend = 1  # overwritten if no constant
    if exog is None and trend == 'c':   # constant only
        exog = np.ones((len(endog), 1))
    elif exog is not None and trend == 'c':  # constant plus exogenous
        exog = add_trend(exog, trend='c', prepend=True, has_constant='raise')
    elif exog is not None and trend == 'nc':
        # make sure it's not holding constant from last run
        if exog.var() == 0:
            exog = None
        k_trend = 0
    if trend == 'nc':
        k_trend = 0
    return k_trend, exog