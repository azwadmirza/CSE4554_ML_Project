def hpre(*content, sep="\n") -> str:
    """
    Make mono-width text block (HTML)

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.pre(
        value=html_decoration.quote(_join(*content, sep=sep))
    )