def imageset(*args):
    r"""
    Return an image of the set under transformation ``f``.

    If this function can't compute the image, it returns an
    unevaluated ImageSet object.

    .. math::
        { f(x) | x \in self }

    Examples
    ========

    >>> from sympy import S, Interval, Symbol, imageset, sin, Lambda
    >>> from sympy.abc import x, y

    >>> imageset(x, 2*x, Interval(0, 2))
    [0, 4]

    >>> imageset(lambda x: 2*x, Interval(0, 2))
    [0, 4]

    >>> imageset(Lambda(x, sin(x)), Interval(-2, 1))
    ImageSet(Lambda(x, sin(x)), [-2, 1])

    >>> imageset(sin, Interval(-2, 1))
    ImageSet(Lambda(x, sin(x)), [-2, 1])
    >>> imageset(lambda y: x + y, Interval(-2, 1))
    ImageSet(Lambda(_x, _x + x), [-2, 1])

    Expressions applied to the set of Integers are simplified
    to show as few negatives as possible and linear expressions
    are converted to a canonical form. If this is not desirable
    then the unevaluated ImageSet should be used.

    >>> imageset(x, -2*x + 5, S.Integers)
    ImageSet(Lambda(x, 2*x + 1), Integers())

    See Also
    ========

    sympy.sets.fancysets.ImageSet

    """
    from sympy.core import Lambda
    from sympy.sets.fancysets import ImageSet
    from sympy.geometry.util import _uniquely_named_symbol

    if len(args) not in (2, 3):
        raise ValueError('imageset expects 2 or 3 args, got: %s' % len(args))

    set = args[-1]
    if not isinstance(set, Set):
        name = func_name(set)
        raise ValueError(
            'last argument should be a set, not %s' % name)

    if len(args) == 3:
        f = Lambda(*args[:2])
    elif len(args) == 2:
        f = args[0]
        if isinstance(f, Lambda):
            pass
        elif (
                isinstance(f, FunctionClass) # like cos
                or func_name(f) == '<lambda>'
                ):
            var = _uniquely_named_symbol(Symbol('x'), f(Dummy()))
            expr = f(var)
            f = Lambda(var, expr)
        else:
            raise TypeError(filldedent('''
        expecting lambda, Lambda, or FunctionClass, not \'%s\'''' %
        func_name(f)))

    r = set._eval_imageset(f)
    if isinstance(r, ImageSet):
        f, set = r.args

    if f.variables[0] == f.expr:
        return set

    if isinstance(set, ImageSet):
        if len(set.lamda.variables) == 1 and len(f.variables) == 1:
            return imageset(Lambda(set.lamda.variables[0],
                                   f.expr.subs(f.variables[0], set.lamda.expr)),
                            set.base_set)

    if r is not None:
        return r

    return ImageSet(f, set)