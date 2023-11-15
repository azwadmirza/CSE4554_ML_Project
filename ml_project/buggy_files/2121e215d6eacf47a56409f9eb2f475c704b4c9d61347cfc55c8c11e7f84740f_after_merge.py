    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.terminator = kwargs.pop('terminator', None)
        super(StartsWith, self).__init__(*args, **kwargs)