def encode(s: Sequence[Tuple[str, str]], similar_to: str=None) -> str:
    """
        Takes a list of (key, value) tuples and returns a urlencoded string.
        If similar_to is passed, the output is formatted similar to the provided urlencoded string.
    """

    remove_trailing_equal = False
    if similar_to:
        remove_trailing_equal = any("=" not in param for param in similar_to.split("&"))

    encoded = urllib.parse.urlencode(s, False, errors="surrogateescape")

    if remove_trailing_equal:
        encoded = encoded.replace("=&", "&")
        if encoded and encoded[-1] == '=':
            encoded = encoded[:-1]

    return encoded