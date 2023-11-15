def ode_nth_linear_euler_eq_nonhomogeneous_undetermined_coefficients(eq, func, order, match, returns='sol'):
    r"""
    Solves an `n`\th order linear non homogeneous Cauchy-Euler equidimensional
    ordinary differential equation using undetermined coefficients.

    This is an equation with form `g(x) = a_0 f(x) + a_1 x f'(x) + a_2 x^2 f''(x)
    \cdots`.

    These equations can be solved in a general manner, by substituting
    solutions of the form `x = exp(t)`, and deriving a characteristic equation
    of form `g(exp(t)) = b_0 f(t) + b_1 f'(t) + b_2 f''(t) \cdots` which can
    be then solved by nth_linear_constant_coeff_undetermined_coefficients if
    g(exp(t)) has finite number of linearly independent derivatives.

    Functions that fit this requirement are finite sums functions of the form
    `a x^i e^{b x} \sin(c x + d)` or `a x^i e^{b x} \cos(c x + d)`, where `i`
    is a non-negative integer and `a`, `b`, `c`, and `d` are constants.  For
    example any polynomial in `x`, functions like `x^2 e^{2 x}`, `x \sin(x)`,
    and `e^x \cos(x)` can all be used.  Products of `\sin`'s and `\cos`'s have
    a finite number of derivatives, because they can be expanded into `\sin(a
    x)` and `\cos(b x)` terms.  However, SymPy currently cannot do that
    expansion, so you will need to manually rewrite the expression in terms of
    the above to use this method.  So, for example, you will need to manually
    convert `\sin^2(x)` into `(1 + \cos(2 x))/2` to properly apply the method
    of undetermined coefficients on it.

    After replacement of x by exp(t), this method works by creating a trial function
    from the expression and all of its linear independent derivatives and
    substituting them into the original ODE.  The coefficients for each term
    will be a system of linear equations, which are be solved for and
    substituted, giving the solution. If any of the trial functions are linearly
    dependent on the solution to the homogeneous equation, they are multiplied
    by sufficient `x` to make them linearly independent.

    Examples
    ========

    >>> from sympy import dsolve, Function, Derivative, log
    >>> from sympy.abc import x
    >>> f = Function('f')
    >>> eq = x**2*Derivative(f(x), x, x) - 2*x*Derivative(f(x), x) + 2*f(x) - log(x)
    >>> dsolve(eq, f(x),
    ... hint='nth_linear_euler_eq_nonhomogeneous_undetermined_coefficients').expand()
    Eq(f(x), C1*x + C2*x**2 + log(x)/2 + 3/4)

    """
    x = func.args[0]
    f = func.func
    r = match

    chareq, eq, symbol = S.Zero, S.Zero, Dummy('x')

    for i in r.keys():
        if not isinstance(i, str) and i >= 0:
            chareq += (r[i]*diff(x**symbol, x, i)*x**-symbol).expand()

    for i in range(1,degree(Poly(chareq, symbol))+1):
        eq += chareq.coeff(symbol**i)*diff(f(x), x, i)

    if chareq.as_coeff_add(symbol)[0]:
        eq += chareq.as_coeff_add(symbol)[0]*f(x)
    e, re = posify(r[-1].subs(x, exp(x)))
    eq += e.subs(re)

    match = _nth_linear_match(eq, f(x), ode_order(eq, f(x)))
    eq_homogeneous = Add(eq,-match[-1])
    match['trialset'] = _undetermined_coefficients_match(match[-1], x, func, eq_homogeneous)['trialset']
    return ode_nth_linear_constant_coeff_undetermined_coefficients(eq, func, order, match).subs(x, log(x)).subs(f(log(x)), f(x)).expand()