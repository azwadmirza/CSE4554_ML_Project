def italic(*content, sep=" "):
    """
    Make italic text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.italic.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )