    def build_info(self):
        # type: () -> int
        if self.run_generic_build('texinfo') > 0:
            return 1
        with cd(self.builddir_join('texinfo')):
            return subprocess.call([self.makecmd, 'info'])