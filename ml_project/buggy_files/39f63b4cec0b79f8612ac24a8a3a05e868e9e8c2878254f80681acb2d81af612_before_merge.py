def format_dict(dict, omit_keys=[], omit_values=[]):
    return ", ".join(
        "{}={}".format(name, str(value))
        for name, value in dict.items()
        if name not in omit_keys and value not in omit_values
    )