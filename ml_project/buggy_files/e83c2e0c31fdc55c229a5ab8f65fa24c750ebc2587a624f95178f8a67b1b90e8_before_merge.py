def unflatten_dict(dt, delimiter="/"):
    """Unflatten dict. Does not support unflattening lists."""
    out = defaultdict(dict)
    for key, val in dt.items():
        path = key.split(delimiter)
        item = out
        for k in path[:-1]:
            item = item[k]
        item[path[-1]] = val
    return dict(out)