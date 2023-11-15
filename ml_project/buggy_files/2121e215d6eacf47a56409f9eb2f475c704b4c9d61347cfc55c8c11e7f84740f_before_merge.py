    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.terminator = kwargs.pop('terminator', None)
        # The details on how to match a bracket are stored in the dialect
        self.start_bracket = Ref('StartBracketSegment')
        self.end_bracket = Ref('EndBracketSegment')
        super(StartsWith, self).__init__(*args, **kwargs)