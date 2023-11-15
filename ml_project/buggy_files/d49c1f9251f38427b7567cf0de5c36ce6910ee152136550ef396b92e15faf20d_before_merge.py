def underline(*content, sep=" "):
    """
    Make underlined text (Markdown)

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.underline.format(
        value=markdown_decoration.quote(_join(*content, sep=sep))
    )