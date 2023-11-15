def _sorted_factors(factors, method):
    """Sort a list of ``(expr, exp)`` pairs. """
    if method == 'sqf':
        def key(obj):
            poly, exp = obj
            rep = poly.rep.rep
            return (exp, len(rep), rep)
    else:
        def key(obj):
            poly, exp = obj
            rep = poly.rep.rep
            return (len(rep), exp, rep)

    return sorted(factors, key=key)