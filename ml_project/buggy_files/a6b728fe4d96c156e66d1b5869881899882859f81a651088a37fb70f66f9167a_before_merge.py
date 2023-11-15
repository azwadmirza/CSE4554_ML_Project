def hitalic(*content, sep=" "):
    """
    Make italic text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.italic.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )