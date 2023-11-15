def hunderline(*content, sep=" ") -> str:
    """
    Make underlined text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.underline(
        value=html_decoration.quote(_join(*content, sep=sep))
    )