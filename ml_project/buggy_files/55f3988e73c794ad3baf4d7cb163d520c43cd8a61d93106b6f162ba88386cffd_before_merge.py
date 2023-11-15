def code_from_code(code):
    """Converts an opensubtitles code to a 3-letter opensubtitles code

    :param code: an opensubtitles language code
    :type code: str
    :return: a 3-letter opensubtitles language code
    :rtype: str
    """

    return from_code(code).opensubtitles