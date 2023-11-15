    def __init__(self, *args):
        # type: (Any) -> None
        if isinstance(args[0], nodes.document) and isinstance(args[1], Builder):
            document, builder = args
        else:
            warnings.warn('The order of arguments for HTML5Translator has been changed. '
                          'Please give "document" as 1st and "builder" as 2nd.',
                          RemovedInSphinx40Warning, stacklevel=2)
            builder, document = args
        super().__init__(document, builder)

        self.highlighter = self.builder.highlighter
        self.docnames = [self.builder.current_docname]  # for singlehtml builder
        self.manpages_url = self.config.manpages_url
        self.protect_literal_text = 0
        self.permalink_text = self.config.html_add_permalinks
        # support backwards-compatible setting to a bool
        if not isinstance(self.permalink_text, str):
            self.permalink_text = self.permalink_text and '¶' or ''
        self.permalink_text = self.encode(self.permalink_text)
        self.secnumber_suffix = self.config.html_secnumber_suffix
        self.param_separator = ''
        self.optional_param_level = 0
        self._table_row_index = 0
        self._fieldlist_row_index = 0
        self.required_params_left = 0