def code(*content, sep=" "):
    """
    Make mono-width text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.code.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )