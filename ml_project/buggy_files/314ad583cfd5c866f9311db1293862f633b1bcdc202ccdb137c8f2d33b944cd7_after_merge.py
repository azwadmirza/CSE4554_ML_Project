def overload_attribute(typ, attr, **kwargs):
    """
    A decorator marking the decorated function as typing and implementing
    attribute *attr* for the given Numba type in nopython mode.

    *kwargs* are passed to the underlying `@overload` call.

    Here is an example implementing .nbytes for array types::

        @overload_attribute(types.Array, 'nbytes')
        def array_nbytes(arr):
            def get(arr):
                return arr.size * arr.itemsize
            return get
    """
    # TODO implement setters
    from .typing.templates import make_overload_attribute_template

    def decorate(overload_func):
        template = make_overload_attribute_template(
            typ, attr, overload_func,
            inline=kwargs.get('inline', 'never'),
        )
        infer_getattr(template)
        overload(overload_func, **kwargs)(overload_func)
        return overload_func

    return decorate