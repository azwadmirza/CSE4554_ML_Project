def _etree_to_dict(t):
    if len(t.getchildren()) > 0:
        d = {}
        for child in t.getchildren():
            d[child.tag] = _etree_to_dict(child)
    else:
        d = t.text
    return d