def from_code(code, unknown='und'):
    """Converts an opensubtitles language code to a proper babelfish.Language object

    :param code: an opensubtitles language code to be converted
    :type code: str
    :param unknown: the code to be returned for unknown language codes
    :type unknown: str
    :return: a language object
    :rtype: babelfish.Language
    """
    code = code.strip()
    if code and code in language_converters['opensubtitles'].codes:
        return Language.fromopensubtitles(code)  # pylint: disable=no-member

    return Language(unknown) if unknown else None