def from_ietf_code(code, unknown='und'):
    """Converts an IETF code to a proper babelfish.Language object

    :param code: an IETF language code
    :type code: str
    :param unknown: the code to be returned for unknown language codes
    :type unknown: str
    :return: a language object
    :rtype: babelfish.Language
    """
    try:
        return Language.fromietf(code)
    except ValueError:
        return Language(unknown) if unknown else None