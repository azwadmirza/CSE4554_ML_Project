def decode_number(value):  # type(string) -> (int)
    """
    Decode string to integer and guess correct base
    :param value: string input value
    :return: integer
    """

    value = value.strip()
    base = 10
    if len(value) > 1 and value[1] == 'b':  # bin coded
        base = 2
        value = value[2:]
    if len(value) > 1 and value[1] == 'x':  # hex coded
        base = 16
        value = value[2:]

    return int(value, base)