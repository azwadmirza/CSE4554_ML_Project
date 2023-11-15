def hstrikethrough(*content, sep=" "):
    """
    Make strikethrough text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.strikethrough.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )