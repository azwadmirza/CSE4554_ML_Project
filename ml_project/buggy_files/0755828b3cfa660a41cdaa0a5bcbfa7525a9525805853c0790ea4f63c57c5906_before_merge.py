def _ctype_ndarray(element_type, shape):
    """ Create an ndarray of the given element type and shape """
    for dim in shape[::-1]:
        element_type = element_type * dim
    return element_type