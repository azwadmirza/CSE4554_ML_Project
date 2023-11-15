def aslist(value):
    """ Cast config values to lists of strings """
    return [item.strip() for item in re.split(",(?![^{]*})",value.strip())]