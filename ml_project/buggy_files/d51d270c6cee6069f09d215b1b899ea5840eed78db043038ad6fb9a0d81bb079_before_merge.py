def overload_method(typ, attr):
    """
    A decorator marking the decorated function as typing and implementing
    attribute *attr* for the given Numba type in nopython mode.

    Here is an example implementing .take() for array types::

        @overload_method(types.Array, 'take')
        def array_take(arr, indices):
            if isinstance(indices, types.Array):
                def take_impl(arr, indices):
                    n = indices.shape[0]
                    res = np.empty(n, arr.dtype)
                    for i in range(n):
                        res[i] = arr[indices[i]]
                    return res
                return take_impl
    """
    from .typing.templates import make_overload_method_template

    def decorate(overload_func):
        template = make_overload_method_template(typ, attr, overload_func)
        infer_getattr(template)
        return overload_func

    return decorate