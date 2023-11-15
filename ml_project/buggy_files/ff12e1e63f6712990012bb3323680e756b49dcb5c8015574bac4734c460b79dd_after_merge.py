    def build(self, **kwargs):
        checkout_path = self.project.checkout_path(self.version.slug)
        build_command = [
            'python',
            self.project.venv_bin(version=self.version.slug, bin='mkdocs'),
            self.builder,
            '--clean',
            '--site-dir', self.build_dir,
        ]
        if self.use_theme:
            build_command.extend(['--theme', 'readthedocs'])
        cmd_ret = self.run(
            *build_command,
            cwd=checkout_path,
            bin_path=self.project.venv_bin(version=self.version.slug, bin=None)
        )
        return cmd_ret.successful