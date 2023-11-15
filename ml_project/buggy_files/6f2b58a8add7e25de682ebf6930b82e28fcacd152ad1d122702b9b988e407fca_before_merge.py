def from_ietf_code(code, unknown='und'):
    """Converts an IETF code to a 3-letter opensubtitles code

    :param code: an IETF language code
    :type code: str
    :param unknown: the code to be returned for unknown language codes
    :type unknown: str
    :return: babelfish.Language
    """
    try:
        return Language.fromietf(code)
    except ValueError:
        return Language(unknown) if unknown else None