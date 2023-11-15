def hitalic(*content, sep=" ") -> str:
    """
    Make italic text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.italic(
        value=html_decoration.quote(_join(*content, sep=sep))
    )