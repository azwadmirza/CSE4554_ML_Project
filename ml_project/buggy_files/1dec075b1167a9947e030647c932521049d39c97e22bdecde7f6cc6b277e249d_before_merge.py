def _read_cookie_pairs(s, off=0):
    """
        Read pairs of lhs=rhs values from Cookie headers.

        off: start offset
    """
    pairs = []

    while True:
        lhs, off = _read_key(s, off)
        lhs = lhs.lstrip()

        if lhs:
            rhs = None
            if off < len(s) and s[off] == "=":
                rhs, off = _read_value(s, off + 1, ";")

            pairs.append([lhs, rhs])

        off += 1

        if not off < len(s):
            break

    return pairs, off