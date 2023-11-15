    def __init__(self, opts, grains, minion_id, saltenv, ext=None, functions=None,
                 pillar=None, pillarenv=None):
        self.opts = opts
        self.opts['environment'] = saltenv
        self.ext = ext
        self.grains = grains
        self.minion_id = minion_id
        self.channel = salt.transport.Channel.factory(opts)
        if pillarenv is not None:
            self.opts['pillarenv'] = pillarenv
        elif self.opts.get('pillarenv_from_saltenv', False):
            self.opts['pillarenv'] = saltenv
        elif 'pillarenv' not in self.opts:
            self.opts['pillarenv'] = None
        self.pillar_override = {}
        if pillar is not None:
            if isinstance(pillar, dict):
                self.pillar_override = pillar
            else:
                log.error('Pillar data must be a dictionary')