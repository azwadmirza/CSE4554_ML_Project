def array_raw_callback(ctx: 'mypy.plugin.AttributeContext') -> Type:
    """Callback to provide an accurate type for ctypes.Array.raw."""
    et = _get_array_element_type(ctx.type)
    if et is not None:
        types = []  # type: List[Type]
        for tp in union_items(et):
            if (isinstance(tp, AnyType)
                    or isinstance(tp, Instance) and tp.type.fullname() == 'ctypes.c_char'):
                types.append(_get_bytes_type(ctx.api))
            else:
                ctx.api.msg.fail(
                    'ctypes.Array attribute "raw" is only available'
                    ' with element type c_char, not "{}"'
                    .format(et),
                    ctx.context)
        return UnionType.make_simplified_union(types)
    return ctx.default_attr_type