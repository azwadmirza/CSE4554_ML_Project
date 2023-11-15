    def __init__(self, execer, ctx, **kwargs):
        super().__init__()
        self.execer = execer
        self.ctx = ctx
        if kwargs.get('completer', True):
            self.completer = Completer()
        self.buffer = []
        self.need_more_lines = False
        self.mlprompt = None
        if HAS_PYGMENTS:
            env = builtins.__xonsh_env__
            self.styler = XonshStyle(env.get('XONSH_COLOR_STYLE'))
        else:
            self.styler = None