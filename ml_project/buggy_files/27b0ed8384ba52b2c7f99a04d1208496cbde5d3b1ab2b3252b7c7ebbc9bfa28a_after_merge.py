def camelResource(obj):
    """Some sources from apis return lowerCased where as describe calls

    always return TitleCase, this function turns the former to the later
    """
    if not isinstance(obj, dict):
        return obj
    for k in list(obj.keys()):
        v = obj.pop(k)
        obj["%s%s" % (k[0].upper(), k[1:])] = v
        if isinstance(v, dict):
            camelResource(v)
        elif isinstance(v, list):
            list(map(camelResource, v))
    return obj