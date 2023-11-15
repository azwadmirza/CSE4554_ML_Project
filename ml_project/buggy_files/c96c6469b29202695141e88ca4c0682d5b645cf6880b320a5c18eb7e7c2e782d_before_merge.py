def classify_ode(eq, func=None, dict=False, ics=None, **kwargs):
    r"""
    Returns a tuple of possible :py:meth:`~sympy.solvers.ode.dsolve`
    classifications for an ODE.

    The tuple is ordered so that first item is the classification that
    :py:meth:`~sympy.solvers.ode.dsolve` uses to solve the ODE by default.  In
    general, classifications at the near the beginning of the list will
    produce better solutions faster than those near the end, thought there are
    always exceptions.  To make :py:meth:`~sympy.solvers.ode.dsolve` use a
    different classification, use ``dsolve(ODE, func,
    hint=<classification>)``.  See also the
    :py:meth:`~sympy.solvers.ode.dsolve` docstring for different meta-hints
    you can use.

    If ``dict`` is true, :py:meth:`~sympy.solvers.ode.classify_ode` will
    return a dictionary of ``hint:match`` expression terms. This is intended
    for internal use by :py:meth:`~sympy.solvers.ode.dsolve`.  Note that
    because dictionaries are ordered arbitrarily, this will most likely not be
    in the same order as the tuple.

    You can get help on different hints by executing
    ``help(ode.ode_hintname)``, where ``hintname`` is the name of the hint
    without ``_Integral``.

    See :py:data:`~sympy.solvers.ode.allhints` or the
    :py:mod:`~sympy.solvers.ode` docstring for a list of all supported hints
    that can be returned from :py:meth:`~sympy.solvers.ode.classify_ode`.

    Notes
    =====

    These are remarks on hint names.

    ``_Integral``

        If a classification has ``_Integral`` at the end, it will return the
        expression with an unevaluated :py:class:`~.Integral`
        class in it.  Note that a hint may do this anyway if
        :py:meth:`~sympy.core.expr.Expr.integrate` cannot do the integral,
        though just using an ``_Integral`` will do so much faster.  Indeed, an
        ``_Integral`` hint will always be faster than its corresponding hint
        without ``_Integral`` because
        :py:meth:`~sympy.core.expr.Expr.integrate` is an expensive routine.
        If :py:meth:`~sympy.solvers.ode.dsolve` hangs, it is probably because
        :py:meth:`~sympy.core.expr.Expr.integrate` is hanging on a tough or
        impossible integral.  Try using an ``_Integral`` hint or
        ``all_Integral`` to get it return something.

        Note that some hints do not have ``_Integral`` counterparts. This is
        because :py:func:`~sympy.integrals.integrals.integrate` is not used in
        solving the ODE for those method. For example, `n`\th order linear
        homogeneous ODEs with constant coefficients do not require integration
        to solve, so there is no
        ``nth_linear_homogeneous_constant_coeff_Integrate`` hint. You can
        easily evaluate any unevaluated
        :py:class:`~sympy.integrals.integrals.Integral`\s in an expression by
        doing ``expr.doit()``.

    Ordinals

        Some hints contain an ordinal such as ``1st_linear``.  This is to help
        differentiate them from other hints, as well as from other methods
        that may not be implemented yet. If a hint has ``nth`` in it, such as
        the ``nth_linear`` hints, this means that the method used to applies
        to ODEs of any order.

    ``indep`` and ``dep``

        Some hints contain the words ``indep`` or ``dep``.  These reference
        the independent variable and the dependent function, respectively. For
        example, if an ODE is in terms of `f(x)`, then ``indep`` will refer to
        `x` and ``dep`` will refer to `f`.

    ``subs``

        If a hints has the word ``subs`` in it, it means the the ODE is solved
        by substituting the expression given after the word ``subs`` for a
        single dummy variable.  This is usually in terms of ``indep`` and
        ``dep`` as above.  The substituted expression will be written only in
        characters allowed for names of Python objects, meaning operators will
        be spelled out.  For example, ``indep``/``dep`` will be written as
        ``indep_div_dep``.

    ``coeff``

        The word ``coeff`` in a hint refers to the coefficients of something
        in the ODE, usually of the derivative terms.  See the docstring for
        the individual methods for more info (``help(ode)``).  This is
        contrast to ``coefficients``, as in ``undetermined_coefficients``,
        which refers to the common name of a method.

    ``_best``

        Methods that have more than one fundamental way to solve will have a
        hint for each sub-method and a ``_best`` meta-classification. This
        will evaluate all hints and return the best, using the same
        considerations as the normal ``best`` meta-hint.


    Examples
    ========

    >>> from sympy import Function, classify_ode, Eq
    >>> from sympy.abc import x
    >>> f = Function('f')
    >>> classify_ode(Eq(f(x).diff(x), 0), f(x))
    ('nth_algebraic', 'separable', '1st_linear', '1st_homogeneous_coeff_best',
    '1st_homogeneous_coeff_subs_indep_div_dep',
    '1st_homogeneous_coeff_subs_dep_div_indep',
    '1st_power_series', 'lie_group',
    'nth_linear_constant_coeff_homogeneous',
    'nth_linear_euler_eq_homogeneous', 'nth_algebraic_Integral',
    'separable_Integral', '1st_linear_Integral',
    '1st_homogeneous_coeff_subs_indep_div_dep_Integral',
    '1st_homogeneous_coeff_subs_dep_div_indep_Integral')
    >>> classify_ode(f(x).diff(x, 2) + 3*f(x).diff(x) + 2*f(x) - 4)
    ('nth_linear_constant_coeff_undetermined_coefficients',
    'nth_linear_constant_coeff_variation_of_parameters',
    'nth_linear_constant_coeff_variation_of_parameters_Integral')

    """
    ics = sympify(ics)

    prep = kwargs.pop('prep', True)

    if func and len(func.args) != 1:
        raise ValueError("dsolve() and classify_ode() only "
        "work with functions of one variable, not %s" % func)

    # Some methods want the unprocessed equation
    eq_orig = eq

    if prep or func is None:
        eq, func_ = _preprocess(eq, func)
        if func is None:
            func = func_
    x = func.args[0]
    f = func.func
    y = Dummy('y')
    xi = kwargs.get('xi')
    eta = kwargs.get('eta')
    terms = kwargs.get('n')

    if isinstance(eq, Equality):
        if eq.rhs != 0:
            return classify_ode(eq.lhs - eq.rhs, func, dict=dict, ics=ics, xi=xi,
                n=terms, eta=eta, prep=False)
        eq = eq.lhs

    order = ode_order(eq, f(x))
    # hint:matchdict or hint:(tuple of matchdicts)
    # Also will contain "default":<default hint> and "order":order items.
    matching_hints = {"order": order}

    df = f(x).diff(x)
    a = Wild('a', exclude=[f(x)])
    b = Wild('b', exclude=[f(x)])
    c = Wild('c', exclude=[f(x)])
    d = Wild('d', exclude=[df, f(x).diff(x, 2)])
    e = Wild('e', exclude=[df])
    k = Wild('k', exclude=[df])
    n = Wild('n', exclude=[x, f(x), df])
    c1 = Wild('c1', exclude=[x])
    a2 = Wild('a2', exclude=[x, f(x), df])
    b2 = Wild('b2', exclude=[x, f(x), df])
    c2 = Wild('c2', exclude=[x, f(x), df])
    d2 = Wild('d2', exclude=[x, f(x), df])
    a3 = Wild('a3', exclude=[f(x), df, f(x).diff(x, 2)])
    b3 = Wild('b3', exclude=[f(x), df, f(x).diff(x, 2)])
    c3 = Wild('c3', exclude=[f(x), df, f(x).diff(x, 2)])
    r3 = {'xi': xi, 'eta': eta}  # Used for the lie_group hint
    boundary = {}  # Used to extract initial conditions
    C1 = Symbol("C1")

    # Preprocessing to get the initial conditions out
    if ics is not None:
        for funcarg in ics:
            # Separating derivatives
            if isinstance(funcarg, (Subs, Derivative)):
                # f(x).diff(x).subs(x, 0) is a Subs, but f(x).diff(x).subs(x,
                # y) is a Derivative
                if isinstance(funcarg, Subs):
                    deriv = funcarg.expr
                    old = funcarg.variables[0]
                    new = funcarg.point[0]
                elif isinstance(funcarg, Derivative):
                    deriv = funcarg
                    # No information on this. Just assume it was x
                    old = x
                    new = funcarg.variables[0]

                if (isinstance(deriv, Derivative) and isinstance(deriv.args[0],
                    AppliedUndef) and deriv.args[0].func == f and
                    len(deriv.args[0].args) == 1 and old == x and not
                    new.has(x) and all(i == deriv.variables[0] for i in
                    deriv.variables) and not ics[funcarg].has(f)):

                    dorder = ode_order(deriv, x)
                    temp = 'f' + str(dorder)
                    boundary.update({temp: new, temp + 'val': ics[funcarg]})
                else:
                    raise ValueError("Enter valid boundary conditions for Derivatives")


            # Separating functions
            elif isinstance(funcarg, AppliedUndef):
                if (funcarg.func == f and len(funcarg.args) == 1 and
                    not funcarg.args[0].has(x) and not ics[funcarg].has(f)):
                    boundary.update({'f0': funcarg.args[0], 'f0val': ics[funcarg]})
                else:
                    raise ValueError("Enter valid boundary conditions for Function")

            else:
                raise ValueError("Enter boundary conditions of the form ics={f(point}: value, f(x).diff(x, order).subs(x, point): value}")

    # Factorable method
    r = _ode_factorable_match(eq, func, kwargs.get('x0', 0))
    if r:
        matching_hints['factorable'] = r

    # Any ODE that can be solved with a combination of algebra and
    # integrals e.g.:
    # d^3/dx^3(x y) = F(x)
    r = _nth_algebraic_match(eq_orig, func)
    if r['solutions']:
        matching_hints['nth_algebraic'] = r
        matching_hints['nth_algebraic_Integral'] = r

    eq = expand(eq)
    # Precondition to try remove f(x) from highest order derivative
    reduced_eq = None
    if eq.is_Add:
        deriv_coef = eq.coeff(f(x).diff(x, order))
        if deriv_coef not in (1, 0):
            r = deriv_coef.match(a*f(x)**c1)
            if r and r[c1]:
                den = f(x)**r[c1]
                reduced_eq = Add(*[arg/den for arg in eq.args])
    if not reduced_eq:
        reduced_eq = eq

    if order == 1:

        ## Linear case: a(x)*y'+b(x)*y+c(x) == 0
        if eq.is_Add:
            ind, dep = reduced_eq.as_independent(f)
        else:
            u = Dummy('u')
            ind, dep = (reduced_eq + u).as_independent(f)
            ind, dep = [tmp.subs(u, 0) for tmp in [ind, dep]]
        r = {a: dep.coeff(df),
             b: dep.coeff(f(x)),
             c: ind}
        # double check f[a] since the preconditioning may have failed
        if not r[a].has(f) and not r[b].has(f) and (
                r[a]*df + r[b]*f(x) + r[c]).expand() - reduced_eq == 0:
            r['a'] = a
            r['b'] = b
            r['c'] = c
            matching_hints["1st_linear"] = r
            matching_hints["1st_linear_Integral"] = r

        ## Bernoulli case: a(x)*y'+b(x)*y+c(x)*y**n == 0
        r = collect(
            reduced_eq, f(x), exact=True).match(a*df + b*f(x) + c*f(x)**n)
        if r and r[c] != 0 and r[n] != 1:  # See issue 4676
            r['a'] = a
            r['b'] = b
            r['c'] = c
            r['n'] = n
            matching_hints["Bernoulli"] = r
            matching_hints["Bernoulli_Integral"] = r

        ## Riccati special n == -2 case: a2*y'+b2*y**2+c2*y/x+d2/x**2 == 0
        r = collect(reduced_eq,
            f(x), exact=True).match(a2*df + b2*f(x)**2 + c2*f(x)/x + d2/x**2)
        if r and r[b2] != 0 and (r[c2] != 0 or r[d2] != 0):
            r['a2'] = a2
            r['b2'] = b2
            r['c2'] = c2
            r['d2'] = d2
            matching_hints["Riccati_special_minus2"] = r

        # NON-REDUCED FORM OF EQUATION matches
        r = collect(eq, df, exact=True).match(d + e * df)
        if r:
            r['d'] = d
            r['e'] = e
            r['y'] = y
            r[d] = r[d].subs(f(x), y)
            r[e] = r[e].subs(f(x), y)

            # FIRST ORDER POWER SERIES WHICH NEEDS INITIAL CONDITIONS
            # TODO: Hint first order series should match only if d/e is analytic.
            # For now, only d/e and (d/e).diff(arg) is checked for existence at
            # at a given point.
            # This is currently done internally in ode_1st_power_series.
            point = boundary.get('f0', 0)
            value = boundary.get('f0val', C1)
            check = cancel(r[d]/r[e])
            check1 = check.subs({x: point, y: value})
            if not check1.has(oo) and not check1.has(zoo) and \
                not check1.has(NaN) and not check1.has(-oo):
                check2 = (check1.diff(x)).subs({x: point, y: value})
                if not check2.has(oo) and not check2.has(zoo) and \
                    not check2.has(NaN) and not check2.has(-oo):
                    rseries = r.copy()
                    rseries.update({'terms': terms, 'f0': point, 'f0val': value})
                    matching_hints["1st_power_series"] = rseries

            r3.update(r)
            ## Exact Differential Equation: P(x, y) + Q(x, y)*y' = 0 where
            # dP/dy == dQ/dx
            try:
                if r[d] != 0:
                    numerator = simplify(r[d].diff(y) - r[e].diff(x))
                    # The following few conditions try to convert a non-exact
                    # differential equation into an exact one.
                    # References : Differential equations with applications
                    # and historical notes - George E. Simmons

                    if numerator:
                        # If (dP/dy - dQ/dx) / Q = f(x)
                        # then exp(integral(f(x))*equation becomes exact
                        factor = simplify(numerator/r[e])
                        variables = factor.free_symbols
                        if len(variables) == 1 and x == variables.pop():
                            factor = exp(Integral(factor).doit())
                            r[d] *= factor
                            r[e] *= factor
                            matching_hints["1st_exact"] = r
                            matching_hints["1st_exact_Integral"] = r
                        else:
                            # If (dP/dy - dQ/dx) / -P = f(y)
                            # then exp(integral(f(y))*equation becomes exact
                            factor = simplify(-numerator/r[d])
                            variables = factor.free_symbols
                            if len(variables) == 1 and y == variables.pop():
                                factor = exp(Integral(factor).doit())
                                r[d] *= factor
                                r[e] *= factor
                                matching_hints["1st_exact"] = r
                                matching_hints["1st_exact_Integral"] = r
                    else:
                        matching_hints["1st_exact"] = r
                        matching_hints["1st_exact_Integral"] = r

            except NotImplementedError:
                # Differentiating the coefficients might fail because of things
                # like f(2*x).diff(x).  See issue 4624 and issue 4719.
                pass

        # Any first order ODE can be ideally solved by the Lie Group
        # method
        matching_hints["lie_group"] = r3

        # This match is used for several cases below; we now collect on
        # f(x) so the matching works.
        r = collect(reduced_eq, df, exact=True).match(d + e*df)
        if r is None and 'factorable' not in matching_hints:
            roots = solve(reduced_eq, df)
            if roots:
                meq = Mul(*[(df - i) for i in roots])*Dummy()
                m = _ode_factorable_match(meq, func, kwargs.get('x0', 0))
                matching_hints['factorable'] = m
        if r:
            # Using r[d] and r[e] without any modification for hints
            # linear-coefficients and separable-reduced.
            num, den = r[d], r[e]  # ODE = d/e + df
            r['d'] = d
            r['e'] = e
            r['y'] = y
            r[d] = num.subs(f(x), y)
            r[e] = den.subs(f(x), y)

            ## Separable Case: y' == P(y)*Q(x)
            r[d] = separatevars(r[d])
            r[e] = separatevars(r[e])
            # m1[coeff]*m1[x]*m1[y] + m2[coeff]*m2[x]*m2[y]*y'
            m1 = separatevars(r[d], dict=True, symbols=(x, y))
            m2 = separatevars(r[e], dict=True, symbols=(x, y))
            if m1 and m2:
                r1 = {'m1': m1, 'm2': m2, 'y': y}
                matching_hints["separable"] = r1
                matching_hints["separable_Integral"] = r1

            ## First order equation with homogeneous coefficients:
            # dy/dx == F(y/x) or dy/dx == F(x/y)
            ordera = homogeneous_order(r[d], x, y)
            if ordera is not None:
                orderb = homogeneous_order(r[e], x, y)
                if ordera == orderb:
                    # u1=y/x and u2=x/y
                    u1 = Dummy('u1')
                    u2 = Dummy('u2')
                    s = "1st_homogeneous_coeff_subs"
                    s1 = s + "_dep_div_indep"
                    s2 = s + "_indep_div_dep"
                    if simplify((r[d] + u1*r[e]).subs({x: 1, y: u1})) != 0:
                        matching_hints[s1] = r
                        matching_hints[s1 + "_Integral"] = r
                    if simplify((r[e] + u2*r[d]).subs({x: u2, y: 1})) != 0:
                        matching_hints[s2] = r
                        matching_hints[s2 + "_Integral"] = r
                    if s1 in matching_hints and s2 in matching_hints:
                        matching_hints["1st_homogeneous_coeff_best"] = r

            ## Linear coefficients of the form
            # y'+ F((a*x + b*y + c)/(a'*x + b'y + c')) = 0
            # that can be reduced to homogeneous form.
            F = num/den
            params = _linear_coeff_match(F, func)
            if params:
                xarg, yarg = params
                u = Dummy('u')
                t = Dummy('t')
                # Dummy substitution for df and f(x).
                dummy_eq = reduced_eq.subs(((df, t), (f(x), u)))
                reps = ((x, x + xarg), (u, u + yarg), (t, df), (u, f(x)))
                dummy_eq = simplify(dummy_eq.subs(reps))
                # get the re-cast values for e and d
                r2 = collect(expand(dummy_eq), [df, f(x)]).match(e*df + d)
                if r2:
                    orderd = homogeneous_order(r2[d], x, f(x))
                    if orderd is not None:
                        ordere = homogeneous_order(r2[e], x, f(x))
                        if orderd == ordere:
                            # Match arguments are passed in such a way that it
                            # is coherent with the already existing homogeneous
                            # functions.
                            r2[d] = r2[d].subs(f(x), y)
                            r2[e] = r2[e].subs(f(x), y)
                            r2.update({'xarg': xarg, 'yarg': yarg,
                                'd': d, 'e': e, 'y': y})
                            matching_hints["linear_coefficients"] = r2
                            matching_hints["linear_coefficients_Integral"] = r2

            ## Equation of the form y' + (y/x)*H(x^n*y) = 0
            # that can be reduced to separable form

            factor = simplify(x/f(x)*num/den)

            # Try representing factor in terms of x^n*y
            # where n is lowest power of x in factor;
            # first remove terms like sqrt(2)*3 from factor.atoms(Mul)
            u = None
            for mul in ordered(factor.atoms(Mul)):
                if mul.has(x):
                    _, u = mul.as_independent(x, f(x))
                    break
            if u and u.has(f(x)):
                h = x**(degree(Poly(u.subs(f(x), y), gen=x)))*f(x)
                p = Wild('p')
                if (u/h == 1) or ((u/h).simplify().match(x**p)):
                    t = Dummy('t')
                    r2 = {'t': t}
                    xpart, ypart = u.as_independent(f(x))
                    test = factor.subs(((u, t), (1/u, 1/t)))
                    free = test.free_symbols
                    if len(free) == 1 and free.pop() == t:
                        r2.update({'power': xpart.as_base_exp()[1], 'u': test})
                        matching_hints["separable_reduced"] = r2
                        matching_hints["separable_reduced_Integral"] = r2

        ## Almost-linear equation of the form f(x)*g(y)*y' + k(x)*l(y) + m(x) = 0
        r = collect(eq, [df, f(x)]).match(e*df + d)
        if r:
            r2 = r.copy()
            r2[c] = S.Zero
            if r2[d].is_Add:
                # Separate the terms having f(x) to r[d] and
                # remaining to r[c]
                no_f, r2[d] = r2[d].as_independent(f(x))
                r2[c] += no_f
            factor = simplify(r2[d].diff(f(x))/r[e])
            if factor and not factor.has(f(x)):
                r2[d] = factor_terms(r2[d])
                u = r2[d].as_independent(f(x), as_Add=False)[1]
                r2.update({'a': e, 'b': d, 'c': c, 'u': u})
                r2[d] /= u
                r2[e] /= u.diff(f(x))
                matching_hints["almost_linear"] = r2
                matching_hints["almost_linear_Integral"] = r2


    elif order == 2:
        # Liouville ODE in the form
        # f(x).diff(x, 2) + g(f(x))*(f(x).diff(x))**2 + h(x)*f(x).diff(x)
        # See Goldstein and Braun, "Advanced Methods for the Solution of
        # Differential Equations", pg. 98

        s = d*f(x).diff(x, 2) + e*df**2 + k*df
        r = reduced_eq.match(s)
        if r and r[d] != 0:
            y = Dummy('y')
            g = simplify(r[e]/r[d]).subs(f(x), y)
            h = simplify(r[k]/r[d]).subs(f(x), y)
            if y in h.free_symbols or x in g.free_symbols:
                pass
            else:
                r = {'g': g, 'h': h, 'y': y}
                matching_hints["Liouville"] = r
                matching_hints["Liouville_Integral"] = r

        # Homogeneous second order differential equation of the form
        # a3*f(x).diff(x, 2) + b3*f(x).diff(x) + c3
        # It has a definite power series solution at point x0 if, b3/a3 and c3/a3
        # are analytic at x0.
        deq = a3*(f(x).diff(x, 2)) + b3*df + c3*f(x)
        r = collect(reduced_eq,
            [f(x).diff(x, 2), f(x).diff(x), f(x)]).match(deq)
        ordinary = False
        if r:
            if not all([r[key].is_polynomial() for key in r]):
                n, d = reduced_eq.as_numer_denom()
                reduced_eq = expand(n)
                r = collect(reduced_eq,
                    [f(x).diff(x, 2), f(x).diff(x), f(x)]).match(deq)
        if r and r[a3] != 0:
            p = cancel(r[b3]/r[a3])  # Used below
            q = cancel(r[c3]/r[a3])  # Used below
            point = kwargs.get('x0', 0)
            check = p.subs(x, point)
            if not check.has(oo, NaN, zoo, -oo):
                check = q.subs(x, point)
                if not check.has(oo, NaN, zoo, -oo):
                    ordinary = True
                    r.update({'a3': a3, 'b3': b3, 'c3': c3, 'x0': point, 'terms': terms})
                    matching_hints["2nd_power_series_ordinary"] = r

            # Checking if the differential equation has a regular singular point
            # at x0. It has a regular singular point at x0, if (b3/a3)*(x - x0)
            # and (c3/a3)*((x - x0)**2) are analytic at x0.
            if not ordinary:
                p = cancel((x - point)*p)
                check = p.subs(x, point)
                if not check.has(oo, NaN, zoo, -oo):
                    q = cancel(((x - point)**2)*q)
                    check = q.subs(x, point)
                    if not check.has(oo, NaN, zoo, -oo):
                        coeff_dict = {'p': p, 'q': q, 'x0': point, 'terms': terms}
                        matching_hints["2nd_power_series_regular"] = coeff_dict
                        # For Hypergeometric solutions.
                _r = {}
                _r.update(r)
                rn = match_2nd_hypergeometric(_r, func)
                if rn:
                    matching_hints["2nd_hypergeometric"] = rn
                    matching_hints["2nd_hypergeometric_Integral"] = rn
            # If the ODE has regular singular point at x0 and is of the form
            # Eq((x)**2*Derivative(y(x), x, x) + x*Derivative(y(x), x) +
            # (a4**2*x**(2*p)-n**2)*y(x) thus Bessel's equation
            rn = match_2nd_linear_bessel(r, f(x))
            if rn:
                matching_hints["2nd_linear_bessel"] = rn

            # If the ODE is ordinary and is of the form of Airy's Equation
            # Eq(x**2*Derivative(y(x),x,x)-(ax+b)*y(x))

            if p.is_zero:
                a4 = Wild('a4', exclude=[x,f(x),df])
                b4 = Wild('b4', exclude=[x,f(x),df])
                rn = q.match(a4+b4*x)
                if rn and rn[b4] != 0:
                    rn = {'b':rn[a4],'m':rn[b4]}
                    matching_hints["2nd_linear_airy"] = rn
    if order > 0:
        # Any ODE that can be solved with a substitution and
        # repeated integration e.g.:
        # `d^2/dx^2(y) + x*d/dx(y) = constant
        #f'(x) must be finite for this to work
        r = _nth_order_reducible_match(reduced_eq, func)
        if r:
            matching_hints['nth_order_reducible'] = r

        # nth order linear ODE
        # a_n(x)y^(n) + ... + a_1(x)y' + a_0(x)y = F(x) = b

        r = _nth_linear_match(reduced_eq, func, order)

        # Constant coefficient case (a_i is constant for all i)
        if r and not any(r[i].has(x) for i in r if i >= 0):
            # Inhomogeneous case: F(x) is not identically 0
            if r[-1]:
                undetcoeff = _undetermined_coefficients_match(r[-1], x)
                s = "nth_linear_constant_coeff_variation_of_parameters"
                matching_hints[s] = r
                matching_hints[s + "_Integral"] = r
                if undetcoeff['test']:
                    r['trialset'] = undetcoeff['trialset']
                    matching_hints[
                        "nth_linear_constant_coeff_undetermined_coefficients"
                            ] = r

            # Homogeneous case: F(x) is identically 0
            else:
                matching_hints["nth_linear_constant_coeff_homogeneous"] = r

        # nth order Euler equation a_n*x**n*y^(n) + ... + a_1*x*y' + a_0*y = F(x)
        #In case of Homogeneous euler equation F(x) = 0
        def _test_term(coeff, order):
            r"""
            Linear Euler ODEs have the form  K*x**order*diff(y(x),x,order) = F(x),
            where K is independent of x and y(x), order>= 0.
            So we need to check that for each term, coeff == K*x**order from
            some K.  We have a few cases, since coeff may have several
            different types.
            """
            if order < 0:
                raise ValueError("order should be greater than 0")
            if coeff == 0:
                return True
            if order == 0:
                if x in coeff.free_symbols:
                    return False
                return True
            if coeff.is_Mul:
                if coeff.has(f(x)):
                    return False
                return x**order in coeff.args
            elif coeff.is_Pow:
                return coeff.as_base_exp() == (x, order)
            elif order == 1:
                return x == coeff
            return False

        # Find coefficient for highest derivative, multiply coefficients to
        # bring the equation into Euler form if possible
        r_rescaled = None
        if r is not None:
            coeff = r[order]
            factor = x**order / coeff
            r_rescaled = {i: factor*r[i] for i in r if i != 'trialset'}

        # XXX: Mixing up the trialset with the coefficients is error-prone.
        # These should be separated as something like r['coeffs'] and
        # r['trialset']

        if r_rescaled and not any(not _test_term(r_rescaled[i], i) for i in
                r_rescaled if i != 'trialset' and i >= 0):
            if not r_rescaled[-1]:
                matching_hints["nth_linear_euler_eq_homogeneous"] = r_rescaled
            else:
                matching_hints["nth_linear_euler_eq_nonhomogeneous_variation_of_parameters"] = r_rescaled
                matching_hints["nth_linear_euler_eq_nonhomogeneous_variation_of_parameters_Integral"] = r_rescaled
                e, re = posify(r_rescaled[-1].subs(x, exp(x)))
                undetcoeff = _undetermined_coefficients_match(e.subs(re), x)
                if undetcoeff['test']:
                    r_rescaled['trialset'] = undetcoeff['trialset']
                    matching_hints["nth_linear_euler_eq_nonhomogeneous_undetermined_coefficients"] = r_rescaled


    # Order keys based on allhints.
    retlist = [i for i in allhints if i in matching_hints]
    if dict:
        # Dictionaries are ordered arbitrarily, so make note of which
        # hint would come first for dsolve().  Use an ordered dict in Py 3.
        matching_hints["default"] = retlist[0] if retlist else None
        matching_hints["ordered_hints"] = tuple(retlist)
        return matching_hints
    else:
        return tuple(retlist)