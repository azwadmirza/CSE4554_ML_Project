def hcode(*content, sep=" "):
    """
    Make mono-width text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.code.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )