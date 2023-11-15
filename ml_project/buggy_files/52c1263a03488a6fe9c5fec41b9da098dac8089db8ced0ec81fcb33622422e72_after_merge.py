def process_array(elt, ascii=False):
    """Process an 'array' tag."""
    del ascii
    chld = list(elt)
    if len(chld) > 1:
        raise ValueError()
    chld = chld[0]
    try:
        name, current_type, scale = CASES[chld.tag](chld)
        size = None
    except ValueError:
        name, current_type, size, scale = CASES[chld.tag](chld)
    del name
    myname = elt.get("name") or elt.get("label")
    if elt.get("length").startswith("$"):
        length = int(VARIABLES[elt.get("length")[1:]])
    else:
        length = int(elt.get("length"))
    if size is not None:
        return (myname, current_type, (length, ) + size, scale)
    else:
        return (myname, current_type, (length, ), scale)