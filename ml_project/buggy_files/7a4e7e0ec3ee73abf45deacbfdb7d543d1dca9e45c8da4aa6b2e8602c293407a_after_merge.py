def impl_new_list(item, allocated=DEFAULT_ALLOCATED):
    """Creates a new list.

    Parameters
    ----------
    item: Numba type
        type of the list item.
    allocated: int
        number of items to pre-allocate

    """
    if not isinstance(item, Type):
        raise TypeError("expecting *item* to be a numba Type")

    itemty = item

    def imp(item, allocated=DEFAULT_ALLOCATED):
        if allocated < 0:
            raise RuntimeError("expecting *allocated* to be >= 0")
        lp = _list_new(itemty, allocated)
        _list_set_method_table(lp, itemty)
        l = _make_list(itemty, lp)
        return l

    return imp