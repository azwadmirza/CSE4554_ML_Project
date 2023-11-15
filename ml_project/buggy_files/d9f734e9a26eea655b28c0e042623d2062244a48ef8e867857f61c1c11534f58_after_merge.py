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
    exception = None

    for encoding in encodings:
        try:
            return str(text.decode(encoding))
        except ValueError as exc:
            exception = exc

    if force:
        for encoding in encodings:
            try:
                return str(text.decode(encoding, 'ignore'))
            except ValueError as exc:
                exception = exc

    raise DecodingError(encodings=encodings, exception=exception, object=text)