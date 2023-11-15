    def __init__(self, opts, pillar=None, jid=None):
        if 'grains' not in opts:
            opts['grains'] = salt.loader.grains(opts)
        self.opts = opts
        self.opts['pillar'] = self.__gather_pillar()
        if pillar and isinstance(pillar, dict):
            self.opts['pillar'].update(pillar)
        self.state_con = {}
        self.load_modules()
        self.active = set()
        self.mod_init = set()
        self.pre = {}
        self.__run_num = 0
        self.jid = jid