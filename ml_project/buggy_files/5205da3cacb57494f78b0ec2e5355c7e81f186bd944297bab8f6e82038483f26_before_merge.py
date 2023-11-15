def _tokenize_mteval_13a(segment):
    r"""
    Tokenizes a string following the tokenizer in mteval-v13a.pl.
    See https://github.com/moses-smt/mosesdecoder/"
           "blob/master/scripts/generic/mteval-v14.pl#L917-L942
    Parameters
    ----------
    segment: str
        A string to be tokenzied

    Returns
    -------
    The tokenized string
    """

    norm = segment.rstrip()

    norm = norm.replace('<skipped>', '')
    norm = norm.replace('-\n', '')
    norm = norm.replace('\n', ' ')
    norm = norm.replace('&quot;', '"')
    norm = norm.replace('&amp;', '&')
    norm = norm.replace('&lt;', '<')
    norm = norm.replace('&gt;', '>')

    norm = ' {} '.format(norm)
    norm = re.sub(r'([\{-\~\[-\` -\&\(-\+\:-\@\/])', ' \\1 ', norm)
    norm = re.sub(r'([^0-9])([\.,])', '\\1 \\2 ', norm)
    norm = re.sub(r'([\.,])([^0-9])', ' \\1 \\2', norm)
    norm = re.sub(r'([0-9])(-)', '\\1 \\2 ', norm)
    norm = re.sub(r'\s+', ' ', norm)
    norm = re.sub(r'^\s+', '', norm)
    norm = re.sub(r'\s+$', '', norm)

    return norm