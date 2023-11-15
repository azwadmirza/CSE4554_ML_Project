def unicode_join(sep, parts):

    if isinstance(parts, types.List):
        if isinstance(parts.dtype, types.UnicodeType):
            def join_list_impl(sep, parts):
                return join_list(sep, parts)
            return join_list_impl
        elif isinstance(parts.dtype, types.UnicodeCharSeq):
            def join_list_impl(sep, parts):
                _parts = [str(p) for p in parts]
                return join_list(sep, _parts)
            return join_list_impl
        else:
            pass  # lists of any other type not supported
    elif isinstance(parts, types.IterableType):
        def join_iter_impl(sep, parts):
            parts_list = [p for p in parts]
            return join_list(sep, parts_list)
        return join_iter_impl
    elif isinstance(parts, types.UnicodeType):
        # Temporary workaround until UnicodeType is iterable
        def join_str_impl(sep, parts):
            parts_list = [parts[i] for i in range(len(parts))]
            return join_list(sep, parts_list)
        return join_str_impl