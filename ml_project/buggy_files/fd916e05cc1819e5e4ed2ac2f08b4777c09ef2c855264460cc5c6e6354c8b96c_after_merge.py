def object_description(object):
    # type: (Any) -> unicode
    """A repr() implementation that returns text safe to use in reST context."""
    if isinstance(object, dict):
        try:
            sorted_keys = sorted(object)
        except Exception:
            pass  # Cannot sort dict keys, fall back to generic repr
        else:
            items = ("%r: %r" % (key, object[key]) for key in sorted_keys)
            return "{%s}" % ", ".join(items)
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