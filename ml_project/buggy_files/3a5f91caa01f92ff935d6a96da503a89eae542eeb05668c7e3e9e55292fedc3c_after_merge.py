    def __init__(self, opts, pillar=None, wrapper=None, fsclient=None):
        self.client = fsclient
        salt.state.BaseHighState.__init__(self, opts)
        self.state = SSHState(opts, pillar, wrapper)
        self.matcher = salt.minion.Matcher(self.opts)
        self.tops = salt.loader.tops(self.opts)

        self._pydsl_all_decls = {}
        self._pydsl_render_stack = []