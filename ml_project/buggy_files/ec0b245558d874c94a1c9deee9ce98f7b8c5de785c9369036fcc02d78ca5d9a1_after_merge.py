def hstrikethrough(*content, sep=" ") -> str:
    """
    Make strikethrough text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.strikethrough(
        value=html_decoration.quote(_join(*content, sep=sep))
    )