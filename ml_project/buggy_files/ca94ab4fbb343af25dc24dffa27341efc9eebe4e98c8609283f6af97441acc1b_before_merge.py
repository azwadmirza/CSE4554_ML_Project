    def __init__(self, opts, grains, minion_id, saltenv, ext=None, functions=None,
                 pillar=None, pillarenv=None, rend=None):
        self.minion_id = minion_id
        self.ext = ext
        if pillarenv is None:
            if opts.get('pillarenv_from_saltenv', False):
                opts['pillarenv'] = saltenv
        # Store the file_roots path so we can restore later. Issue 5449
        self.actual_file_roots = opts['file_roots']
        # use the local file client
        self.opts = self.__gen_opts(opts, grains, saltenv=saltenv, pillarenv=pillarenv)
        self.saltenv = saltenv
        self.client = salt.fileclient.get_file_client(self.opts, True)

        if opts.get('file_client', '') == 'local':
            opts['grains'] = grains

        # if we didn't pass in functions, lets load them
        if functions is None:
            utils = salt.loader.utils(opts)
            if opts.get('file_client', '') == 'local':
                self.functions = salt.loader.minion_mods(opts, utils=utils)
            else:
                self.functions = salt.loader.minion_mods(self.opts, utils=utils)
        else:
            self.functions = functions

        self.matcher = salt.minion.Matcher(self.opts, self.functions)
        if rend is None:
            self.rend = salt.loader.render(self.opts, self.functions)
        else:
            self.rend = rend
        ext_pillar_opts = copy.deepcopy(self.opts)
        # Fix self.opts['file_roots'] so that ext_pillars know the real
        # location of file_roots. Issue 5951
        ext_pillar_opts['file_roots'] = self.actual_file_roots
        # Keep the incoming opts ID intact, ie, the master id
        if 'id' in opts:
            ext_pillar_opts['id'] = opts['id']
        self.merge_strategy = 'smart'
        if opts.get('pillar_source_merging_strategy'):
            self.merge_strategy = opts['pillar_source_merging_strategy']

        self.ext_pillars = salt.loader.pillars(ext_pillar_opts, self.functions)
        self.ignored_pillars = {}
        self.pillar_override = {}
        if pillar is not None:
            if isinstance(pillar, dict):
                self.pillar_override = pillar
            else:
                log.error('Pillar data must be a dictionary')