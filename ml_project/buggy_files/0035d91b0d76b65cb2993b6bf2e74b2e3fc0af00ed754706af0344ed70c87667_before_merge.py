    def __init__(self, src, dest, file_args, module):
        self.src = src
        self.dest = dest
        self.file_args = file_args
        self.opts = module.params['extra_opts']
        self.module = module
        if self.module.check_mode:
            self.module.exit_json(skipped=True, msg="remote module (%s) does not support check mode when using gtar" % self.module._name)
        self.excludes = [path.rstrip('/') for path in self.module.params['exclude']]
        # Prefer gtar (GNU tar) as it supports the compression options -z, -j and -J
        self.cmd_path = self.module.get_bin_path('gtar', None)
        if not self.cmd_path:
            # Fallback to tar
            self.cmd_path = self.module.get_bin_path('tar')
        self.zipflag = '-z'
        self._files_in_archive = []

        if self.cmd_path:
            self.tar_type = self._get_tar_type()
        else:
            self.tar_type = None