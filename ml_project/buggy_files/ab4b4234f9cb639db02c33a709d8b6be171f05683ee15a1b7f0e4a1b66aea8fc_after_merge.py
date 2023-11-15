def _extend_row(row, names, items, precision):
    def _round(val):
        if isinstance(val, float):
            return round(val, precision)

        return val

    if not items:
        row.extend(["-"] * len(names))
        return

    for fname, item in items:
        if isinstance(item, dict):
            item = flatten(item)
        else:
            item = {fname: item}
        for name in names:
            if name in item:
                value = item[name]
                text = str(_round(value)) if value is not None else "-"
                row.append(text)
            else:
                row.append("-")