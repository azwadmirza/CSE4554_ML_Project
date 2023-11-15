def format_dict(dict_like, omit_keys=[], omit_values=[]):
    from snakemake.io import Namedlist

    if isinstance(dict_like, Namedlist):
        items = dict_like.items()
    elif isinstance(dict_like, dict):
        items = dict_like.items()
    else:
        raise ValueError(
            "bug: format_dict applied to something neither a dict nor a Namedlist"
        )
    return ", ".join(
        "{}={}".format(name, str(value))
        for name, value in items
        if name not in omit_keys and value not in omit_values
    )