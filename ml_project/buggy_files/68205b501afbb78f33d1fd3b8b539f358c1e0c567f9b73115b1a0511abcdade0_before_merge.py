    def __init__(self, opts, grains, id_, env, ext=None):
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
        self.ext_pillars = salt.loader.pillars(self.opts, self.functions)