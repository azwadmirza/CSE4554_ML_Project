def get_conditionally_linear_system(eqs, variables=None):
    '''
    Convert equations into a linear system using sympy.
    
    Parameters
    ----------
    eqs : `Equations`
        The model equations.
    
    Returns
    -------
    coefficients : dict of (sympy expression, sympy expression) tuples
        For every variable x, a tuple (M, B) containing the coefficients M and
        B (as sympy expressions) for M * x + B
    
    Raises
    ------
    ValueError
        If one of the equations cannot be converted into a M * x + B form.

    Examples
    --------
    >>> from brian2 import Equations
    >>> eqs = Equations("""
    ... dv/dt = (-v + w**2) / tau : 1
    ... dw/dt = -w / tau : 1
    ... """)
    >>> system = get_conditionally_linear_system(eqs)
    >>> print(system['v'])
    (-1/tau, w**2.0/tau)
    >>> print(system['w'])
    (-1/tau, 0)

    '''
    diff_eqs = eqs.get_substituted_expressions(variables)
    
    coefficients = {}
    
    for name, expr in diff_eqs:
        var = sp.Symbol(name, real=True)
    
        s_expr = str_to_sympy(expr.code, variables).expand()
        if s_expr.has(var):
            # Factor out the variable
            s_expr = sp.collect(s_expr,
                                var, evaluate=False)

            if len(s_expr) > 2 or var not in s_expr:
                raise ValueError(('The expression "%s", defining the variable %s, '
                                 'could not be separated into linear components') %
                                 (expr, name))
            coefficients[name] = (s_expr[var], s_expr.get(1, 0))
        else:
            coefficients[name] = (0, s_expr)

    return coefficients