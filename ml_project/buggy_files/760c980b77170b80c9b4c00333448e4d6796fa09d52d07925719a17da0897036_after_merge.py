def hcode(*content, sep=" ") -> str:
    """
    Make mono-width text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.code(
        value=html_decoration.quote(_join(*content, sep=sep))
    )