def impl_copy(l):
    itemty = l.item_type
    if isinstance(l, types.ListType):
        def impl(l):
            newl = new_list(itemty, len(l))
            for i in l:
                newl.append(i)
            return newl

        return impl