def _update_names(names, items):
    for name, item in items:
        if isinstance(item, dict):
            item = flatten(item)
            names.update(item.keys())
        else:
            names.add(name)