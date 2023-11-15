def jscode(expr, assign_to=None, **settings):
    """Converts an expr to a string of javascript code

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
           are their string representations. Alternatively the
           dictionary values can be a list of tuples i.e. [(argument_test,
           jsfunction_string)].
       human : optional
           If True, the result is a single string that may contain some
           constant declarations for the number symbols. If False, the
           same information is returned in a more programmer-friendly
           data structure.

       Examples
       ========

       >>> from sympy import jscode, symbols, Rational, sin
       >>> x, tau = symbols(["x", "tau"])
       >>> jscode((2*tau)**Rational(7,2))
       '8*Math.sqrt(2)*Math.pow(tau, 7/2)'
       >>> jscode(sin(x), assign_to="s")
       's = Math.sin(x);'

    """
    return JavascriptCodePrinter(settings).doprint(expr, assign_to)