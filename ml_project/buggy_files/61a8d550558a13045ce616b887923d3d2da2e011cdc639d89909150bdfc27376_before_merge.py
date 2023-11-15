    def __init__(
            self,
            opts,
            pillar=None,
            jid=None,
            pillar_enc=None,
            proxy=None,
            context=None,
            mocked=False,
            loader='states'):
        self.opts = opts
        self.client = salt.fileclient.get_file_client(self.opts)
        BaseHighState.__init__(self, opts)
        self.state = State(
                           self.opts,
                           pillar,
                           jid,
                           pillar_enc,
                           proxy=proxy,
                           context=context,
                           mocked=mocked,
                           loader=loader)
        self.matcher = salt.minion.Matcher(self.opts)

        # tracks all pydsl state declarations globally across sls files
        self._pydsl_all_decls = {}

        # a stack of current rendering Sls objects, maintained and used by the pydsl renderer.
        self._pydsl_render_stack = []