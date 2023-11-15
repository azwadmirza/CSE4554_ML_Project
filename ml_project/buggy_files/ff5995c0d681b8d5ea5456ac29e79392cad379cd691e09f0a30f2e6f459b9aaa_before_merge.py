def impl_copy(l):
    if isinstance(l, types.ListType):
        def impl(l):
            return l[:]

        return impl