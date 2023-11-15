    def pred(part):
        # true when slice does *not* reduce, False when part is a tuple,
        # i.e. MultiIndex slice
        return ((isinstance(part, slice) or is_list_like(part))
                and not isinstance(part, tuple))