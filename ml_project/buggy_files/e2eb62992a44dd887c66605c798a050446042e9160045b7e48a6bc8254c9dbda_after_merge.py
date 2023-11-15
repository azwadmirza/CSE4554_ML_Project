def new_list(item, allocated=DEFAULT_ALLOCATED):
    """Construct a new list. (Not implemented in the interpreter yet)

    Parameters
    ----------
    item: TypeRef
        Item type of the new list.
    allocated: int
        number of items to pre-allocate

    """
    # With JIT disabled, ignore all arguments and return a Python list.
    return list()