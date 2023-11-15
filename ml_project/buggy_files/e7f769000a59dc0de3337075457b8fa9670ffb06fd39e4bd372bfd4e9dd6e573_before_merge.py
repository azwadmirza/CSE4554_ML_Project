def fcode(expr, assign_to=None, **settings):
    """Converts an expr to a string of Fortran 77 code

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
           are there string representations.
       human : optional
           If True, the result is a single string that may contain some
           parameter statements for the number symbols. If False, the same
           information is returned in a more programmer-friendly data
           structure.
       source_format : optional
           The source format can be either 'fixed' or 'free'.
           [default='fixed']
       standard : optional
           The Fortran standard to be followed. This is specified as an integer.
           Acceptable standards are 66, 77, 90, 95, 2003, and 2008. Default is
           77. Note that currently the only distinction internally is between
           standards before 95, and those 95 and after. This may change later
           as more features are added.
       contract: optional
           If True, `Indexed` instances are assumed to obey
           tensor contraction rules and the corresponding nested
           loops over indices are generated. Setting contract = False
           will not generate loops, instead the user is responsible
           to provide values for the indices in the code. [default=True]

       Examples
       ========

       >>> from sympy import fcode, symbols, Rational, pi, sin
       >>> x, tau = symbols('x,tau')
       >>> fcode((2*tau)**Rational(7,2))
       '      8*sqrt(2.0d0)*tau**(7.0d0/2.0d0)'
       >>> fcode(sin(x), assign_to="s")
       '      s = sin(x)'
       >>> print(fcode(pi))
             parameter (pi = 3.14159265358979d0)
             pi
       >>> from sympy import Eq, IndexedBase, Idx
       >>> len_y = 5
       >>> y = IndexedBase('y', shape=(len_y,))
       >>> t = IndexedBase('t', shape=(len_y,))
       >>> Dy = IndexedBase('Dy', shape=(len_y-1,))
       >>> i = Idx('i', len_y-1)
       >>> e=Eq(Dy[i], (y[i+1]-y[i])/(t[i+1]-t[i]))
       >>> fcode(e.rhs, assign_to=e.lhs, contract=False)
       '      Dy(i) = (y(i + 1) - y(i))/(t(i + 1) - t(i))'

    """
    # run the printer
    return FCodePrinter(settings).doprint(expr, assign_to)