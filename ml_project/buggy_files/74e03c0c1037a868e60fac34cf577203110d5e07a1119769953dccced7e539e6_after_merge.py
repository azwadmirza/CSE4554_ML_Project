def _format_pairs(pairs, specials=(), sep="; "):
    """
        specials: A lower-cased list of keys that will not be quoted.
    """
    vals = []
    for k, v in pairs:
        if k.lower() not in specials and _has_special(v):
            v = ESCAPE.sub(r"\\\1", v)
            v = '"%s"' % v
        vals.append("%s=%s" % (k, v))
    return sep.join(vals)