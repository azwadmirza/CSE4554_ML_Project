def build_preprocessors(md, **kwargs):
    """ Build the default set of preprocessors used by Markdown. """
    preprocessors = util.Registry()
    preprocessors.register(NormalizeWhitespace(md), 'normalize_whitespace', 30)
    preprocessors.register(HtmlBlockPreprocessor(md), 'html_block', 20)
    preprocessors.register(ReferencePreprocessor(md), 'reference', 10)
    return preprocessors