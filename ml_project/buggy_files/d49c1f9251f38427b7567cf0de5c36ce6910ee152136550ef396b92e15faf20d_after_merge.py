def underline(*content, sep=" ") -> str:
    """
    Make underlined text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.underline(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )