def _etree_to_dict(t):
    list_t = list(t)
    if len(list_t) > 0:
        d = {}
        for child in list_t:
            d[child.tag] = _etree_to_dict(child)
    else:
        d = t.text
    return d