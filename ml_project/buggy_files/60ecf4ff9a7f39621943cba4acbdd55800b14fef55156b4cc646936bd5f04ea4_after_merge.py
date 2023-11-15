    def empty_list(cls, item_type, allocated=DEFAULT_ALLOCATED):
        """Create a new empty List.

        Parameters
        ----------
        item_type: Numba type
            type of the list item.
        allocated: int
            number of items to pre-allocate
        """
        if config.DISABLE_JIT:
            return list()
        else:
            return cls(lsttype=ListType(item_type), allocated=allocated)