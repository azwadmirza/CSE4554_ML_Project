def bold(*content, sep=" ") -> str:
    """
    Make bold text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.bold(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )