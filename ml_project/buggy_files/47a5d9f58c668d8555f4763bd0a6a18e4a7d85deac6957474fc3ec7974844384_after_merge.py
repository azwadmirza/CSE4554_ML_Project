def record_from_name(name):
    """Search `dastcom.idx` and return logical records that match a given string.

    Body name, SPK-ID, or alternative designations can be used.

    Parameters
    ----------
    name : str
        Body name.

    Returns
    -------
    records : list (int)
        DASTCOM5 database logical records matching str.

    """
    records = []
    lines = string_record_from_name(name)
    for line in lines:
        records.append(int(line[:8].lstrip()))
    return records