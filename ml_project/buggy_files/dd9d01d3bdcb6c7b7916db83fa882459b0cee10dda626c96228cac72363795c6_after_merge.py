def walk_tree(base, map=None):
    # type: (Any, Any) -> None
    """
    the routine here walks over a simple yaml tree (recursing in
    dict values and list items) and converts strings that
    have multiple lines to literal scalars

    You can also provide an explicit (ordered) mapping for multiple transforms
    (first of which is executed):
        map = ruamel.yaml.compat.ordereddict
        map['\n'] = preserve_literal
        map[':'] = SingleQuotedScalarString
        walk_tree(data, map=map)
    """
    from dynaconf.vendor.ruamel.yaml.compat import string_types
    from dynaconf.vendor.ruamel.yaml.compat import MutableMapping, MutableSequence  # type: ignore

    if map is None:
        map = {'\n': preserve_literal}

    if isinstance(base, MutableMapping):
        for k in base:
            v = base[k]  # type: Text
            if isinstance(v, string_types):
                for ch in map:
                    if ch in v:
                        base[k] = map[ch](v)
                        break
            else:
                walk_tree(v)
    elif isinstance(base, MutableSequence):
        for idx, elem in enumerate(base):
            if isinstance(elem, string_types):
                for ch in map:
                    if ch in elem:  # type: ignore
                        base[idx] = map[ch](elem)
                        break
            else:
                walk_tree(elem)