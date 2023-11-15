    def __init__(self, src, b_dest, file_args, module):
        self.src = src
        self.b_dest = b_dest
        self.file_args = file_args
        self.opts = module.params['extra_opts']
        self.module = module
        self.excludes = module.params['exclude']
        self.includes = []
        self.cmd_path = self.module.get_bin_path('unzip')
        self.zipinfocmd_path = self.module.get_bin_path('zipinfo')
        self._files_in_archive = []
        self._infodict = dict()