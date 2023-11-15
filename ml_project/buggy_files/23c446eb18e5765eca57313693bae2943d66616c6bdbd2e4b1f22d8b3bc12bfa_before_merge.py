def strikethrough(*content, sep=" "):
    """
    Make strikethrough text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.strikethrough.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )