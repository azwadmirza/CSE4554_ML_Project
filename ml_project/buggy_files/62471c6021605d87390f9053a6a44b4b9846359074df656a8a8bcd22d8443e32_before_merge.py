    def __init__(self, *args, **kwargs):
        if 'delimiter' not in kwargs:
            raise ValueError("Delimited grammars require a `delimiter`")
        self.delimiter = kwargs.pop('delimiter')
        self.allow_trailing = kwargs.pop('allow_trailing', False)
        self.terminator = kwargs.pop('terminator', None)
        # Setting min delimiters means we have to match at least this number
        self.min_delimiters = kwargs.pop('min_delimiters', None)

        # The details on how to match a bracket are stored in the dialect
        self.start_bracket = Ref('StartBracketSegment')
        self.end_bracket = Ref('EndBracketSegment')
        super(Delimited, self).__init__(*args, **kwargs)