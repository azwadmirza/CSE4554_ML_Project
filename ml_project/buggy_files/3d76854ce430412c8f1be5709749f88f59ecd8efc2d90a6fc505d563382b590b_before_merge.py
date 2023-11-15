    def imp(item, allocated=0):
        if allocated < 0:
            raise RuntimeError("expecting *allocated* to be >= 0")
        lp = _list_new(itemty, allocated)
        _list_set_method_table(lp, itemty)
        l = _make_list(itemty, lp)
        return l