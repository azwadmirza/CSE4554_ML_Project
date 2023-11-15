def _make_list(itemty, allocated=0):
    return listobject._as_meminfo(listobject.new_list(itemty,
                                                      allocated=allocated))