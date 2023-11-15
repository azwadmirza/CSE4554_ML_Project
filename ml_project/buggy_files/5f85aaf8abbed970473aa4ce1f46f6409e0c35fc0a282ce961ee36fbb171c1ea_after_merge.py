def hbold(*content, sep=" ") -> str:
    """
    Make bold text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.bold(
        value=html_decoration.quote(_join(*content, sep=sep))
    )