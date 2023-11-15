def pre(*content, sep="\n") -> str:
    """
    Make mono-width text block (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.pre(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )