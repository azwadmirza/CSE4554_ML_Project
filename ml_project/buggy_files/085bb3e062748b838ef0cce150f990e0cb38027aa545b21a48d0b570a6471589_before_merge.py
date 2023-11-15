def validate_axis(axis, tileable=None):
    if axis == 'index':
        axis = 0
    elif axis == 'columns':
        axis = 1

    illegal = False
    try:
        axis = operator.index(axis)
        if axis < 0 or (tileable and axis >= tileable.ndim):
            illegal = True
    except TypeError:
        illegal = True

    if illegal:
        raise ValueError('No axis named {} for '
                         'object type {}'.format(axis, type(tileable)))
    return axis