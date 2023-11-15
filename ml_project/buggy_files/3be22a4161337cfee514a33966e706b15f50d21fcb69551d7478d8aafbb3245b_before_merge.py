def pre(*content, sep="\n"):
    """
    Make mono-width text block (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.pre.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )