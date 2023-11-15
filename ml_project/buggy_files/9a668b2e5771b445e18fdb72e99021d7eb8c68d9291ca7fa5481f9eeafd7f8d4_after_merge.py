def _read_set_cookie_pairs(s: str, off=0) -> Tuple[List[TPairs], int]:
    """
        Read pairs of lhs=rhs values from SetCookie headers while handling multiple cookies.

        off: start offset
        specials: attributes that are treated specially
    """
    cookies = []  # type: List[TPairs]
    pairs = []  # type: TPairs

    while True:
        lhs, off = _read_key(s, off, ";=,")
        lhs = lhs.lstrip()

        rhs = ""
        if off < len(s) and s[off] == "=":
            rhs, off = _read_value(s, off + 1, ";,")

            # Special handling of attributes
            if lhs.lower() == "expires":
                # 'expires' values can contain commas in them so they need to
                # be handled separately.

                # We actually bank on the fact that the expires value WILL
                # contain a comma. Things will fail, if they don't.

                # '3' is just a heuristic we use to determine whether we've
                # only read a part of the expires value and we should read more.
                if len(rhs) <= 3:
                    trail, off = _read_value(s, off + 1, ";,")
                    rhs = rhs + "," + trail
        if rhs or lhs:
            pairs.append([lhs, rhs])

            # comma marks the beginning of a new cookie
            if off < len(s) and s[off] == ",":
                cookies.append(pairs)
                pairs = []

        off += 1

        if not off < len(s):
            break

    if pairs or not cookies:
        cookies.append(pairs)

    return cookies, off