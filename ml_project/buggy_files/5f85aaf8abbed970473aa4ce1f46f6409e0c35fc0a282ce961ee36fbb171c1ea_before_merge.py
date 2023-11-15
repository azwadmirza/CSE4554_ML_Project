def hbold(*content, sep=" "):
    """
    Make bold text (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.bold.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )