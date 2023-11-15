def _make_list(itemty, allocated=DEFAULT_ALLOCATED):
    return listobject._as_meminfo(listobject.new_list(itemty,
                                                      allocated=allocated))