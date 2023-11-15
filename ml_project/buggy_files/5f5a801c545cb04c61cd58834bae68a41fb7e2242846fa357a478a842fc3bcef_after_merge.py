def impl_extend(l, iterable):
    if not isinstance(l, types.ListType):
        return
    if not isinstance(iterable, types.IterableType):
        raise TypingError("extend argument must be iterable")

    _check_for_none_typed(l, 'extend')

    def select_impl():
        if isinstance(iterable, types.ListType):
            def impl(l, iterable):
                if not l._is_mutable():
                    raise ValueError("list is immutable")
                # guard against l.extend(l)
                if l is iterable:
                    iterable = iterable.copy()
                for i in iterable:
                    l.append(i)

            return impl
        else:
            def impl(l, iterable):
                for i in iterable:
                    l.append(i)

            return impl

    if l.is_precise():
        # Handle the precise case.
        return select_impl()
    else:
        # Handle the imprecise case, try to 'guess' the underlying type of the
        # values in the iterable.
        if hasattr(iterable, "dtype"):  # tuples and arrays
            ty = iterable.dtype
        elif hasattr(iterable, "item_type"):  # lists
            ty = iterable.item_type
        elif hasattr(iterable, "yield_type"):  # iterators and generators
            ty = iterable.yield_type
        elif isinstance(iterable, types.UnicodeType):
            ty = iterable
        else:
            raise TypingError("unable to extend list, iterable is missing "
                              "either *dtype*, *item_type* or *yield_type*.")
        l = l.refine(ty)
        # Create the signature that we wanted this impl to have
        sig = typing.signature(types.void, l, iterable)
        return sig, select_impl()