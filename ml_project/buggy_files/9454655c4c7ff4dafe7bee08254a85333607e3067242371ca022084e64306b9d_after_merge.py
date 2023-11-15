def code(*content, sep=" ") -> str:
    """
    Make mono-width text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.code(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )