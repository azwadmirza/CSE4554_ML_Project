def summary_params_2dflat(result, endog_names=None, exog_names=None, alpha=0.95,
                          use_t=True, keep_headers=True, endog_cols=False):
                          #skip_headers2=True):
    '''summary table for parameters that are 2d, e.g. multi-equation models

    Parameter
    ---------
    result : result instance
        the result instance with params, bse, tvalues and conf_int
    endog_names : None or list of strings
        names for rows of the parameter array (multivariate endog)
    exog_names : None or list of strings
        names for columns of the parameter array (exog)
    alpha : float
        level for confidence intervals, default 0.95
    use_t : bool
        indicator whether the p-values are based on the Student-t
        distribution (if True) or on the normal distribution (if False)
    keep_headers : bool
        If true (default), then sub-tables keep their headers. If false, then
        only the first headers are kept, the other headerse are blanked out
    endog_cols : bool
        If false (default) then params and other result statistics have
        equations by rows. If true, then equations are assumed to be in columns.
        Not implemented yet.

    Returns
    -------
    tables : list of SimpleTable
        this contains a list of all seperate Subtables
    table_all : SimpleTable
        the merged table with results concatenated for each row of the parameter
        array

    '''

    res = result
    params = res.params
    if params.ndim == 2: # we've got multiple equations
        n_equ = params.shape[1]
        if not len(endog_names) == params.shape[1]:
            raise ValueError('endog_names has wrong length')
    else:
        if not len(endog_names) == len(params):
            raise ValueError('endog_names has wrong length')
        n_equ = 1

    #VAR doesn't have conf_int
    #params = res.params.T # this is a convention for multi-eq models

    if not isinstance(endog_names, list):
        #this might be specific to multinomial logit type, move?
        if endog_names is None:
            endog_basename = 'endog'
        else:
            endog_basename = endog_names
        #TODO: note, the [1:] is specific to current MNLogit
        endog_names = res.model.endog_names[1:]

    #check if we have the right length of names

    tables = []
    for eq in range(n_equ):
        restup = (res, res.params[:,eq], res.bse[:,eq], res.tvalues[:,eq],
                  res.pvalues[:,eq], res.conf_int(alpha)[eq])

        #not used anymore in current version
#        if skip_headers2:
#            skiph = (row != 0)
#        else:
#            skiph = False
        skiph = False
        tble = summary_params(restup, yname=endog_names[eq],
                              xname=exog_names, alpha=.05, use_t=use_t,
                              skip_header=skiph)

        tables.append(tble)

    #add titles, they will be moved to header lines in table_extend
    for i in range(len(endog_names)):
        tables[i].title = endog_names[i]

    table_all = table_extend(tables, keep_headers=keep_headers)

    return tables, table_all