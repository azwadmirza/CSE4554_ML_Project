def quote_html(*content, sep=" ") -> str:
    """
    Quote HTML symbols

    All <, >, & and " symbols that are not a part of a tag or
    an HTML entity must be replaced with the corresponding HTML entities
    (< with &lt; > with &gt; & with &amp and " with &quot).

    :param content:
    :param sep:
    :return:
    """
    return html_decoration.quote(_join(*content, sep=sep))