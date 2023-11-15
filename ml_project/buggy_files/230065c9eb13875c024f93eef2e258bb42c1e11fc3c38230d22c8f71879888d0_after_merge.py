def highest_precedence_type(exprs):
    # Return the highest precedence type from the passed expressions. Also
    # verifies that there are valid implicit casts between any of the types and
    # the selected highest precedence type
    if not exprs:
        raise ValueError('Must pass at least one expression')

    type_counts = Counter(expr.type() for expr in exprs)
    scores = (
        (_TYPE_PRECEDENCE[k.name.lower()], k) for k, v in type_counts.items()
    )
    _, highest_type = max(scores, key=first)

    for expr in exprs:
        if not expr._can_cast_implicit(highest_type):
            raise TypeError(
                'Expression with type {0} cannot be implicitly casted to {1}'
                .format(expr.type(), highest_type)
            )

    return highest_type