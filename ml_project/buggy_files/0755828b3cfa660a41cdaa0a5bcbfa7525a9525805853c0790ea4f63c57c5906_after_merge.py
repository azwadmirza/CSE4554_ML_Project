    def _ctype_ndarray(element_type, shape):
        """ Create an ndarray of the given element type and shape """
        for dim in shape[::-1]:
            element_type = dim * element_type
            # prevent the type name include np.ctypeslib
            element_type.__module__ = None
        return element_type