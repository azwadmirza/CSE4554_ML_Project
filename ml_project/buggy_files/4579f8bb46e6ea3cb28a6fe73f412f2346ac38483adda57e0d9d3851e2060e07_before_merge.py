def hpre(*content, sep="\n"):
    """
    Make mono-width text block (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.pre.format(
        value=html_decoration.quote(_join(*content, sep=sep))
    )