def hunderline(*content, sep=" "):
    """
    Make underlined text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.underline.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )