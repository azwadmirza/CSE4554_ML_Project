def dynamic_time(seconds) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if d > 0:
        msg = "{0}d {1}h"
    elif d == 0 and h > 0:
        msg = "{1}h {2}m"
    elif d == 0 and h == 0 and m > 0:
        msg = "{2}m {3}s"
    elif d == 0 and h == 0 and m == 0 and s > 0:
        msg = "{3}s"
    else:
        msg = ""
    return msg.format(d, h, m, s)