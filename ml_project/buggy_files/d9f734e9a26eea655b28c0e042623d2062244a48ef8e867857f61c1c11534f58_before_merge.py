def decode(text: Union[bytes, str], encodings: Sequence[str] = ("utf-8",),
           force: bool = False) -> str:
    """
    Decode given string to UTF-8 (default).

    Parameters:
        text: if unicode string is given, same object is returned
        encodings: list/tuple of encodings to use
        force: Ignore invalid characters

    Returns:
        converted unicode string

    Raises:
        ValueError: if decoding failed
    """
    if isinstance(text, str):
        return text

    for encoding in encodings:
        try:
            return str(text.decode(encoding))
        except ValueError:
            pass

    if force:
        for encoding in encodings:
            try:
                return str(text.decode(encoding, 'ignore'))
            except ValueError:
                pass

    raise ValueError("Could not decode string with given encodings{!r}"
                     ".".format(encodings))