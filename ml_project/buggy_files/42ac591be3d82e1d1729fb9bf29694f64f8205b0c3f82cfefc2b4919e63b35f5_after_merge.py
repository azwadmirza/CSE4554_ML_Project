    def __init__(self, opts, pillar=None, jid=None):
        if 'grains' not in opts:
            opts['grains'] = salt.loader.grains(opts)
        self.opts = opts
        self._pillar_override = pillar
        self.opts['pillar'] = self._gather_pillar()
        self.state_con = {}
        self.load_modules()
        self.active = set()
        self.mod_init = set()
        self.pre = {}
        self.__run_num = 0
        self.jid = jid