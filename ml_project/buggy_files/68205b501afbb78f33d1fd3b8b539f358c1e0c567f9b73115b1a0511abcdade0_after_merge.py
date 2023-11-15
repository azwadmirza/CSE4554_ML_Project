    def __init__(self, opts, grains, id_, env, ext=None):
        # Store the file_roots path so we can restore later. Issue 5449
        self.actual_file_roots = opts['file_roots']
        # use the local file client
        self.opts = self.__gen_opts(opts, grains, id_, env, ext)
        self.client = salt.fileclient.get_file_client(self.opts)
        if opts.get('file_client', '') == 'local':
            opts['grains'] = grains
            self.functions = salt.loader.minion_mods(opts)
        else:
            self.functions = salt.loader.minion_mods(self.opts)
        self.matcher = salt.minion.Matcher(self.opts, self.functions)
        self.rend = salt.loader.render(self.opts, self.functions)
        # Fix self.opts['file_roots'] so that ext_pillars know the real
        # location of file_roots. Issue 5951
        ext_pillar_opts = dict(self.opts)
        ext_pillar_opts['file_roots'] = self.actual_file_roots
        self.ext_pillars = salt.loader.pillars(ext_pillar_opts, self.functions)