def _update_names(names, items):
    from flatten_json import flatten

    for name, item in items:
        if isinstance(item, dict):
            item = flatten(item, ".")
            names.update(item.keys())
        else:
            names.add(name)