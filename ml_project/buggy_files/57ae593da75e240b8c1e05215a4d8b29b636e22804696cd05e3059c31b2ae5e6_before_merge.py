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
        self.states_loader = loader
        if 'grains' not in opts:
            opts['grains'] = salt.loader.grains(opts)
        self.opts = opts
        self.proxy = proxy
        self._pillar_override = pillar
        if pillar_enc is not None:
            try:
                pillar_enc = pillar_enc.lower()
            except AttributeError:
                pillar_enc = str(pillar_enc).lower()
            if pillar_enc not in VALID_PILLAR_ENC:
                raise SaltInvocationError(
                    'Invalid pillar encryption type. Valid types are: {0}'
                    .format(', '.join(VALID_PILLAR_ENC))
                )
        self._pillar_enc = pillar_enc
        self.opts['pillar'] = self._gather_pillar()
        self.state_con = context or {}
        self.load_modules(proxy=proxy)
        self.active = set()
        self.mod_init = set()
        self.pre = {}
        self.__run_num = 0
        self.jid = jid
        self.instance_id = str(id(self))
        self.inject_globals = {}
        self.mocked = mocked