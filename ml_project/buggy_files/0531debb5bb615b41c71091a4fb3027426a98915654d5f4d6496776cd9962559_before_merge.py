def convert_to_bytes(param):
    """
    This method convert units to bytes, which follow IEC standard.

    :param param: value to be converted
    """
    if param is None:
        return None

    # Get rid of whitespaces:
    param = ''.join(param.split())

    # Convert to bytes:
    if param[-3].lower() in ['k', 'm', 'g', 't', 'p']:
        return int(param[:-3]) * BYTES_MAP.get(param[-3:].lower(), 1)
    elif param.isdigit():
        return int(param) * 2**10
    else:
        raise ValueError(
            "Unsupported value(IEC supported): '{value}'".format(value=param)
        )