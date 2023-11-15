def fractions(min_value=None, max_value=None, max_denominator=None):
    """Returns a strategy which generates Fractions.

    If min_value is not None then all generated values are no less than
    min_value.

    If max_value is not None then all generated values are no greater than
    max_value.

    If max_denominator is not None then the absolute value of the denominator
    of any generated values is no greater than max_denominator. Note that
    max_denominator must be at least 1.

    """
    check_valid_bound(min_value, 'min_value')
    check_valid_bound(max_value, 'max_value')
    check_valid_interval(min_value, max_value, 'min_value', 'max_value')

    check_valid_integer(max_denominator)
    if max_denominator is not None and max_denominator < 1:
        raise InvalidArgument(
            u'Invalid denominator bound %s' % max_denominator
        )

    denominator_strategy = integers(min_value=1, max_value=max_denominator)

    def dm_func(denom):
        max_num = max_value * denom if max_value is not None else None
        min_num = min_value * denom if min_value is not None else None

        return builds(
            Fraction,
            integers(min_value=min_num, max_value=max_num),
            just(denom)
        )

    return denominator_strategy.flatmap(dm_func)