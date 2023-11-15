    def build_latexpdfja(self):
        # type: () -> int
        if self.run_generic_build('latex') > 0:
            return 1
        try:
            with cd(self.builddir_join('latex')):
                return subprocess.call([self.makecmd, 'all-pdf-ja'])
        except OSError:
            print('Error: Failed to run: %s' % self.makecmd)
            return 1