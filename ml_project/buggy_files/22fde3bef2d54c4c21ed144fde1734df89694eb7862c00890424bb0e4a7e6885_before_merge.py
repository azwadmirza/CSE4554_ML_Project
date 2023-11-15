def name_from_code(code):
    """Returns the language name for the given language code

    :param code: the opensubtitles language code
    :type code: str
    :return: the language name
    :rtype: str
    """
    return from_code(code).name