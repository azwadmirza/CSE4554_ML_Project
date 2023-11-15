def _flatten_result(my_dict: dict, sep: str = ":") -> dict:
    """
    Flatten two-level dictionary

    Use keys in the first level as a prefix for keys in the two levels.
    For example,
    my_dict = { "a": { "b": 7 } } 
    flatten(my_dict)
    { "a:b": 7 }


    :param dict my_dict: contains stats dictionary
    :param str sep: separator between the two keys (default: ":")

    :return: a one-level dictionary with key combined
    :rtype: dict[str, float | str]
    """
    items = []
    for k1, kv2 in my_dict.items():
        for k2, v in kv2.items():
            new_key = f"{k1}{sep}{k2}"
            items.append((new_key, v))

    return dict(items)