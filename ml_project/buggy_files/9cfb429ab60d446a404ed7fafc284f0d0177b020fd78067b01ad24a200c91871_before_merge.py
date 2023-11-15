def ccode(expr, assign_to=None, **settings):
    r"""Converts an expr to a string of c code

        Parameters
        ==========

        expr : sympy.core.Expr
            a sympy expression to be converted
        assign_to : optional
            When given, the argument is used as the name of the
            variable to which the Fortran expression is assigned.
            (This is helpful in case of line-wrapping.)
        precision : optional
            the precision for numbers such as pi [default=15]
        user_functions : optional
            A dictionary where keys are FunctionClass instances and values
            are their string representations.  Alternatively, the
            dictionary value can be a list of tuples i.e. [(argument_test,
            cfunction_string)].  See below for examples.
        human : optional
            If True, the result is a single string that may contain some
            constant declarations for the number symbols. If False, the
            same information is returned in a more programmer-friendly
            data structure.
        contract: optional
            If True, `Indexed` instances are assumed to obey
            tensor contraction rules and the corresponding nested
            loops over indices are generated. Setting contract = False
            will not generate loops, instead the user is responsible
            to provide values for the indices in the code. [default=True]


        Examples
        ========

        >>> from sympy import ccode, symbols, Rational, sin, ceiling, Abs
        >>> x, tau = symbols(["x", "tau"])
        >>> ccode((2*tau)**Rational(7,2))
        '8*sqrt(2)*pow(tau, 7.0L/2.0L)'
        >>> ccode(sin(x), assign_to="s")
        's = sin(x);'
        >>> custom_functions = {
        ...   "ceiling": "CEIL",
        ...   "Abs": [(lambda x: not x.is_integer, "fabs"),
        ...           (lambda x: x.is_integer, "ABS")]
        ... }
        >>> ccode(Abs(x) + ceiling(x), user_functions=custom_functions)
        'fabs(x) + CEIL(x)'
        >>> from sympy import Eq, IndexedBase, Idx
        >>> len_y = 5
        >>> y = IndexedBase('y', shape=(len_y,))
        >>> t = IndexedBase('t', shape=(len_y,))
        >>> Dy = IndexedBase('Dy', shape=(len_y-1,))
        >>> i = Idx('i', len_y-1)
        >>> e=Eq(Dy[i], (y[i+1]-y[i])/(t[i+1]-t[i]))
        >>> ccode(e.rhs, assign_to=e.lhs, contract=False)
        'Dy[i] = (y[i + 1] - y[i])/(t[i + 1] - t[i]);'

    """
    return CCodePrinter(settings).doprint(expr, assign_to)