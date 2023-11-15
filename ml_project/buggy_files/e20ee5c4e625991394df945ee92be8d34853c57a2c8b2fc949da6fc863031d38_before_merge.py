def object_description(object):
    # type: (Any) -> unicode
    """A repr() implementation that returns text safe to use in reST context."""
    if isinstance(object, dict):
        try:
            sorted_keys = sorted(object)
        except TypeError:
            pass  # Cannot sort dict keys, fall back to generic repr
        else:
            items = ("%s: %s" %
                     (object_description(key), object_description(object[key]))
                     for key in sorted_keys)
            return "{%s}" % ", ".join(items)
    if isinstance(object, set):
        try:
            sorted_values = sorted(object)
        except TypeError:
            pass  # Cannot sort set values, fall back to generic repr
        else:
            template = "{%s}" if PY3 else "set([%s])"
            return template % ", ".join(object_description(x)
                                        for x in sorted_values)
    try:
        s = repr(object)
    except Exception:
        raise ValueError
    if isinstance(s, binary_type):
        s = force_decode(s, None)  # type: ignore
    # Strip non-deterministic memory addresses such as
    # ``<__main__.A at 0x7f68cb685710>``
    s = memory_address_re.sub('', s)
    return s.replace('\n', ' ')