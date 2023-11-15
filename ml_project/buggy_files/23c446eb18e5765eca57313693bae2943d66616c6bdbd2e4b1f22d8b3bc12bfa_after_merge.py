def strikethrough(*content, sep=" ") -> str:
    """
    Make strikethrough text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.strikethrough(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )