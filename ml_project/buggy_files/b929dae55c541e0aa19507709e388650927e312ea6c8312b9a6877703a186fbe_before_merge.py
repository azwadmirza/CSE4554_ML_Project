def bold(*content, sep=" "):
    """
    Make bold text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.bold.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )