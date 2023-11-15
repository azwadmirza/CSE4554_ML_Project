def fractions(min_value=None, max_value=None, max_denominator=None):
    """Returns a strategy which generates Fractions.

    If min_value is not None then all generated values are no less than
    min_value.  If max_value is not None then all generated values are no
    greater than max_value.  min_value and max_value may be anything accepted
    by the `python:`~fractions.Fraction` constructor.

    If max_denominator is not None then the denominator of any generated
    values is no greater than max_denominator. Note that max_denominator must
    be None or a positive integer.

    """
    if min_value is not None:
        min_value = Fraction(min_value)
    if max_value is not None:
        max_value = Fraction(max_value)

    check_valid_bound(min_value, 'min_value')
    check_valid_bound(max_value, 'max_value')
    check_valid_interval(min_value, max_value, 'min_value', 'max_value')
    check_valid_integer(max_denominator)

    if max_denominator is not None:
        if max_denominator < 1:
            raise InvalidArgument(
                'max_denominator=%r must be >= 1' % max_denominator)

        def fraction_bounds(value):
            """Find the best lower and upper approximation for value."""
            # Adapted from CPython's Fraction.limit_denominator here:
            # https://github.com/python/cpython/blob/3.6/Lib/fractions.py#L219
            if value is None or value.denominator <= max_denominator:
                return value, value
            p0, q0, p1, q1 = 0, 1, 1, 0
            n, d = value.numerator, value.denominator
            while True:
                a = n // d
                q2 = q0 + a * q1
                if q2 > max_denominator:
                    break
                p0, q0, p1, q1 = p1, q1, p0 + a * p1, q2
                n, d = d, n - a * d
            k = (max_denominator - q0) // q1
            low, high = Fraction(p1, q1), Fraction(p0 + k * p1, q0 + k * q1)
            assert low < value < high
            return low, high

        # Take the high approximation for min_value and low for max_value
        bounds = (max_denominator, min_value, max_value)
        _, min_value = fraction_bounds(min_value)
        max_value, _ = fraction_bounds(max_value)

        if None not in (min_value, max_value) and min_value > max_value:
            raise InvalidArgument(
                'There are no fractions with a denominator <= %r between '
                'min_value=%r and max_value=%r' % bounds)

    if min_value is not None and min_value == max_value:
        return just(min_value)

    def dm_func(denom):
        """Take denom, construct numerator strategy, and build fraction."""
        # Four cases of algebra to get integer bounds and scale factor.
        min_num, max_num = None, None
        if max_value is None and min_value is None:
            pass
        elif min_value is None:
            max_num = denom * max_value.numerator
            denom *= max_value.denominator
        elif max_value is None:
            min_num = denom * min_value.numerator
            denom *= min_value.denominator
        else:
            low = min_value.numerator * max_value.denominator
            high = max_value.numerator * min_value.denominator
            scale = min_value.denominator * max_value.denominator
            # After calculating our integer bounds and scale factor, we remove
            # the gcd to avoid drawing more bytes for the example than needed.
            # Note that `div` can be at most equal to `scale`.
            div = gcd(scale, gcd(low, high))
            min_num = denom * low // div
            max_num = denom * high // div
            denom *= scale // div

        return builds(
            Fraction,
            integers(min_value=min_num, max_value=max_num),
            just(denom)
        )

    if max_denominator is None:
        return integers(min_value=1).flatmap(dm_func)

    return integers(1, max_denominator).flatmap(dm_func).map(
        lambda f: f.limit_denominator(max_denominator))