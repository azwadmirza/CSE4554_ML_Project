def italic(*content, sep=" ") -> str:
    """
    Make italic text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.italic(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )