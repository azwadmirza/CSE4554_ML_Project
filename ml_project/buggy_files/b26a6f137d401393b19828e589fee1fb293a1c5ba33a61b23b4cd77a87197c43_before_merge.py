def swap_memory():
    """System swap memory as (total, used, free, sin, sout) namedtuple."""
    pagesize = 1 if OPENBSD else PAGESIZE
    total, used, free, sin, sout = [x * pagesize for x in cext.swap_mem()]
    percent = usage_percent(used, total, _round=1)
    return _common.sswap(total, used, free, percent, sin, sout)