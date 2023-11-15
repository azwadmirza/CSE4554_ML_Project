def diophantine(eq, param=symbols("t", integer=True)):
    """
    Simplify the solution procedure of diophantine equation ``eq`` by
    converting it into a product of terms which should equal zero.

    For example, when solving, `x^2 - y^2 = 0` this is treated as
    `(x + y)(x - y) = 0` and `x+y = 0` and `x-y = 0` are solved independently
    and combined. Each term is solved by calling ``diop_solve()``.

    Output of ``diophantine()`` is a set of tuples. Each tuple represents a
    solution of the input equation. In a tuple, solution for each variable is
    listed according to the alphabetic order of input variables. i.e. if we have
    an equation with two variables `a` and `b`, first element of the tuple will
    give the solution for `a` and the second element will give the solution for
    `b`.

    Usage
    =====

    ``diophantine(eq, t)``: Solve the diophantine equation ``eq``.
    ``t`` is the parameter to be used by ``diop_solve()``.

    Details
    =======

    ``eq`` should be an expression which is assumed to be zero.
    ``t`` is the parameter to be used in the solution.

    Examples
    ========

    >>> from sympy.solvers.diophantine import diophantine
    >>> from sympy.abc import x, y, z
    >>> diophantine(x**2 - y**2)
    set([(-t_0, -t_0), (t_0, -t_0)])

    #>>> diophantine(x*(2*x + 3*y - z))
    #set([(0, n1, n2), (3*t - z, -2*t + z, z)])
    #>>> diophantine(x**2 + 3*x*y + 4*x)
    #set([(0, n1), (3*t - 4, -t)])

    See Also
    ========

    diop_solve()
    """
    if isinstance(eq, Eq):
        eq = eq.lhs - eq.rhs

    eq = Poly(eq).as_expr()
    if not eq.is_polynomial() or eq.is_number:
        raise TypeError("Equation input format not supported")

    var = list(eq.expand(force=True).free_symbols)
    var.sort(key=default_sort_key)

    terms = factor_list(eq)[1]

    sols = set([])

    for term in terms:

        base = term[0]

        var_t, jnk, eq_type = classify_diop(base)
        if not var_t:
            continue
        solution = diop_solve(base, param)

        if eq_type in ["linear", "homogeneous_ternary_quadratic", "general_pythagorean"]:
            if merge_solution(var, var_t, solution) != ():
                sols.add(merge_solution(var, var_t, solution))

        elif eq_type in ["binary_quadratic",  "general_sum_of_squares", "univariate"]:
            for sol in solution:
                if merge_solution(var, var_t, sol) != ():
                    sols.add(merge_solution(var, var_t, sol))

    return sols